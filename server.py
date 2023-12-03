from flask import Flask, request
from flask_socketio import SocketIO, emit
from TTS.api import TTS
import logging
import base64
import io
from faster_whisper import WhisperModel
from openai import OpenAI

client = OpenAI(api_key='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')

app = Flask(__name__)
app.logger.setLevel(logging.ERROR)

socketio = SocketIO(app, logger=True, engineio_logger=True)

# Initialize TTS and Whisper models
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda")
tts_model = tts.synthesizer.tts_model
gpt_cond_latent, speaker_embedding = tts_model.get_conditioning_latents(audio_path=["female.wav"])

whisper_model_size = "tiny.en"
whisper_model = WhisperModel(whisper_model_size, device="cuda", compute_type="float32")

def process_text(text, sid, socketio):
    try:
        print('Processing text:', text)
        stream_generator = tts_model.inference_stream(
            text,
            "en",
            gpt_cond_latent,
            speaker_embedding,
            stream_chunk_size=3,
            overlap_wav_len=64,
        )

        for audio_chunk in stream_generator:
            # Process and send the audio data
            audio_data = audio_chunk.squeeze().unsqueeze(0).cpu().numpy().tobytes()
            print('Emitting audio')
            socketio.emit('audio_chunk', {'data': audio_data}, to=sid)
    except Exception as e:
        print(f"Error during TTS inference: {e}")
        socketio.emit('error', {'message': str(e)}, to=sid)

@socketio.on('transcribe')
def handle_transcription(json):
    sid = request.sid
    data = base64.b64decode(json['data'])
    audio_data = io.BytesIO(data)
    try:
        segments, _ = whisper_model.transcribe(audio_data, temperature=0, beam_size=2)
        full_text = ''
        for segment in segments:
            emit('transcribed_text', {'text': segment.text}, to=sid)
            full_text += segment.text
        # call chatgpt API
        socketio.start_background_task(chatWithGPT, full_text, sid, socketio)
    except Exception as e:
        emit('error', {'message': str(e)}, to=sid)
        print(f"Error in transcription: {e}")


def chatWithGPT(text, sid, socketio):
    print("CHATGPT TEXT:", text)
    gpt_stream = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[{"role": "user", "content": text}],
        stream=True,
    )
    full_output = ''
    output_chunk = ''
    for chunk in gpt_stream:
        output = chunk.choices[0].delta.content
        if output is not None:
            output_chunk += output
            full_output += output
        if any(output_chunk.strip().endswith(delimiter) for delimiter in
               ['.', '?', '!', ';', '\n']) or output == None:
            if len(output_chunk) <= 2:
                break

            socketio.start_background_task(process_text, output_chunk, sid, socketio)
            output_chunk = ''
    print("CHATGPT OUTPUT:", full_output)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000) 

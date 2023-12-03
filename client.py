import socketio
import base64
import io
import wave
import pyaudio
import argparse
from queue import Queue
from threading import Thread
import time
import threading

# SocketIO client setup
sio = socketio.Client()

audio_queue_response = Queue()


# PyAudio setup
p = pyaudio.PyAudio()
playback_stream = p.open(format=pyaudio.paFloat32,
                         channels=1,
                         rate=24000,
                         output=True)

def audio_player_thread():
    """ Thread to play audio chunks from the queue """
    while True:
        data = audio_queue_response.get()
        if data is None:
            break  # Signal to terminate
        try:
            playback_stream.write(data)
        except Exception as e:
            print(f"Error playing audio: {e}")
    playback_stream.stop_stream()
    playback_stream.close()
    p.terminate()


def handle_audio_chunk(data):
    """ Add received audio chunk to the queue """
    try:
        # Depending on how the server sends the data, you may need to process it here
        processed_data = data  # Replace this with any necessary processing
        audio_queue_response.put(processed_data)
    except Exception as e:
        print(f"Error handling audio chunk: {e}")


@sio.event
def connect():
    print("Connected to server")

@sio.event
def disconnect():
    print("Disconnected from server")

@sio.on('audio_chunk')
def on_audio_chunk(data):
    handle_audio_chunk(data['data'])



def send_audio_data(audio_queue):
    while True:
        audio_bytes = audio_queue.get()
        if audio_bytes is None:
            break

        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(audio_bytes)

        audio_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        sio.emit('transcribe', {'data': audio_base64})

def record_audio(audio_queue, record_seconds):
    audio_format = pyaudio.paInt16
    channels = 1
    sample_rate = 16000
    chunk = 1024

    stream = p.open(format=audio_format, channels=channels,
                    rate=sample_rate, input=True,
                    frames_per_buffer=chunk)

    print("Recording...")

    frames = []
    for _ in range(0, int(sample_rate / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)

    print("Finished recording.")

    stream.stop_stream()
    stream.close()

    audio_bytes = b''.join(frames)
    audio_queue.put(audio_bytes)
    audio_queue.put(None)

    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--record_seconds", type=int, default=5, help="Duration of recording in seconds")
    args = parser.parse_args()

    audio_queue = Queue()

    sio.connect('ws://127.0.0.1:5000')  # Update with your Flask server URL

    Thread(target=record_audio, args=(audio_queue, args.record_seconds)).start()
    Thread(target=send_audio_data, args=(audio_queue,)).start()
    player_thread = threading.Thread(target=audio_player_thread)
    player_thread.start()

    time.sleep(15)  # Adjust as necessary for remaining audio
    audio_queue_response.put(None)  # Signal to terminate the player thread
    player_thread.join()



if __name__ == "__main__":
    main()

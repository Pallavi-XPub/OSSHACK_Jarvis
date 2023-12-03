JARVIS - AI-Based Conversational Assistant

Description
JARVIS is an AI-based conversational assistant that leverages cutting-edge open-source models for speech-to-text (STT) and text-to-speech (TTS) tasks. Designed to provide a seamless conversational experience, JARVIS is capable of understanding natural language input through voice and responding with synthesized speech. The project includes a user-friendly Streamlit-based GUI, allowing users to interact with JARVIS using voice commands.

Features
1. Speech Recognition: Utilizes advanced STT models to accurately transcribe user speech into text.
2. Conversational AI: Employs OpenAI's GPT model for natural language understanding and generation.
3. Text-to-Speech: Converts JARVIS's textual responses back into lifelike speech using state-of-the-art TTS models.
4. Streamlit GUI: Simple and intuitive interface for voice recording and receiving audio responses.

Installation
To set up JARVIS on your local machine:

Clone the Repository:
git clone [URL of the JARVIS repository]

Install Dependencies:
pip install -r requirements.txt


Usage
To start JARVIS:

Start the server:
python3 server.py

Run the Streamlit App:
streamlit run main.py

Interacting with JARVIS:

Open the Streamlit GUI in your web browser.
Use the 'Record' button to start speaking to JARVIS.
Wait for the response from JARVIS, which will be played back through the speakers.

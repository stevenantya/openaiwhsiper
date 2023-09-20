from dotenv import load_dotenv
import os
import openai

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

openai.api_key = os.getenv("OPENAI_API_KEY")
audio_file = open("audio1.mp3", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file)
print(transcript)
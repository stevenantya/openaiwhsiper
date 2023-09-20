import serial
import numpy as np
from scipy.io.wavfile import write
from dotenv import load_dotenv
import os
import openai
import time
import requests
import json

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

openai.api_key = os.getenv("OPENAI_API_KEY")


SAMPLE_RATE = 4000  # Must match the Arduino's sample rate
DURATION = 10  # Duration of recording in seconds

# Set up serial connection (modify the COM port accordingly)
ser = serial.Serial('/dev/ttyACM0', 250000)
data = []

print("Recording...")
for _ in range(SAMPLE_RATE * DURATION):
    try:
        line = ser.readline().decode('utf-8').strip()
        value = int(line)
        data.append(value)
    except:
        pass

print("Saving...")
data = np.array(data, dtype=np.int16)
write("output.wav", SAMPLE_RATE, data)
ser.close()

time.sleep(5)
audio_file = open("output.wav", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file)
print(transcript)

def get_location(speech_data):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "There is 6 location: A,B,C,D,E,Table. I want you to determine what location should I go to. Respond by giving the letter only e.g. A"},
            {"role": "user", "content": "I am having a meeting in location B. Let us go there now!"},
            {"role": "assistant", "content": "A"},
            {"role": "user", "content": speech_data}
        ]
    )
    return response['choices'][0]['message']['content']

goal_url = "http://192.168.201.100/api/NaviBee/robottask"

# Define the locations
locations = ['A', 'B', 'C', 'D', 'E', 'Table']

data = {}  # Dictionary to hold the content of the JSON files for each location

# Loop over each location to open and read the JSON files
for location in locations:
    with open(f'Robot_API_GPT/location_{location}.json', 'r') as file:
        data[location] = json.load(file)

next_location = get_location(transcript['text'])
response = requests.post(goal_url, json= data[next_location])

post_response_json = response.json()
print(next_location)
print(response.status_code)
print(post_response_json)
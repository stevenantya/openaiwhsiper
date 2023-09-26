import serial
import numpy as np
from scipy.io.wavfile import write
from dotenv import load_dotenv
import os
import openai
import time
import keyboard
import uuid
import requests
import json

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

openai.api_key = os.getenv("OPENAI_API_KEY")

#press r to start recording
SAMPLE_RATE = 4000  # Must match the Arduino's sample rate

# Set up serial connection (modify the COM port accordingly)
ser = serial.Serial('COM5', 250000)
data = []

print("Press 'r' to start recording...")

# Wait until 'r' is pressed to start recording
keyboard.wait('r')

print("Recording... Press 'r' again to stop.")
time.sleep(0.5)  # Introduce a small delay

while True:
    try:
        line = ser.readline().decode('utf-8').strip()
        value = int(line)
        data.append(value)
    except:
        pass
    
    # Check if 'r' is pressed to stop recording
    if keyboard.is_pressed('r'):
        break

print("Saving...")
data = np.array(data, dtype=np.int16)
write("output.wav", SAMPLE_RATE, data)
ser.close()

"""
SAMPLE_RATE = 4000  # Must match the Arduino's sample rate
DURATION = 10  # Duration of recording in seconds

# Set up serial connection (modify the COM port accordingly)
ser = serial.Serial('COM5', 250000)
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
"""

time.sleep(5)
audio_file = open("output.wav", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file)
print(transcript)

def get_location(speech_data):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "There are 3      locations: Meeting Room,Entrance,Table. I want you to determine what location should I go to, infer to your best understanding. Respond by giving the exact location e.g. Meeting Room. I can give the prompt in any language! Answer everything in English! e.g. 會議室 is Meeting Room"},
            {"role": "user", "content": "I am having a meeting in the Meeting Room. Let us go there now!"},
            {"role": "assistant", "content": "Meeting Room"},
            {"role": "user", "content": "今天有开会在会议室， 一起去会议室吧!"},
            {"role": "assistant", "content": "Meeting Room"},
            {"role": "user", "content": "诶你有时间吗？ 有啊，怎么了？ 我想讨论下上星期的工作内容。 好啊， 走吧。"},
            {"role": "assistant", "content": "Meeting Room"},
            {"role": "user", "content": speech_data}
        ]
    )
    return response['choices'][0]['message']['content']

goal_url = "http://192.168.192.100/api/NaviBee/robottask"

# Define the locations
locations = ['Meeting Room', 'Entrance', 'C', 'D', 'E', 'Table']

data = {}  # Dictionary to hold the content of the JSON files for each location

# Loop over each location to open and read the JSON files

for location in locations:
    with open(f'Robot_API_GPT/location_{location}.json', 'r') as file:
        data[location] = json.load(file)
    
    # Update the 'jobid' with a new UUID
    data[location]['jobid'] = str(uuid.uuid4())

next_location = get_location(transcript['text'])
response = requests.post(goal_url, json= data[next_location])

post_response_json = response.json()
print(next_location)
print(response.status_code)
print(post_response_json)
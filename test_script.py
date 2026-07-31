import requests
import time
import sys

BASE_URL = "http://localhost:8000"

import os

def test_flow():
    print("1. Uploading test audio...")
    audio_path = os.path.join(os.path.dirname(__file__), "test_audio.wav")
    with open(audio_path, "rb") as f:
        response = requests.post(f"{BASE_URL}/api/songs/upload", files={"file": f})
    
    if response.status_code != 200:
        print(f"Upload failed: {response.text}")
        sys.exit(1)
        
    data = response.json()
    song_id = data["song_id"]
    print(f"Upload successful. Song ID: {song_id}")
    
    print("2. Waiting for processing to complete...")
    while True:
        response = requests.get(f"{BASE_URL}/api/songs/{song_id}")
        if response.status_code != 200:
            print(f"Failed to get song status: {response.text}")
            sys.exit(1)
            
        song_data = response.json()
        status = song_data["status"]
        print(f"Current status: {status}")
        
        if status == "completed":
            print("Processing completed successfully!")
            break
        elif status == "error":
            print("Processing failed!")
            sys.exit(1)
            
        time.sleep(5)
        
    print("3. Testing pitch shift...")
    response = requests.post(f"{BASE_URL}/api/songs/{song_id}/pitch-shift?semitones=2&stem=vocals")
    if response.status_code != 200:
        print(f"Pitch shift failed: {response.text}")
        sys.exit(1)
        
    pitch_data = response.json()
    print(f"Pitch shift successful. URL: {pitch_data['url']}")
    print("All tests passed!")

if __name__ == "__main__":
    test_flow()

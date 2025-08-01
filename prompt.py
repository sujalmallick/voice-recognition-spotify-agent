import requests      # To send commands to FastAPI backend
import json          # To handle response data
import speech_recognition as sr  # For microphone & speech-to-text

# Your FastAPI endpoint
API_URL = "http://localhost:8000/command"  # Change this if hosted elsewhere

# 🎉 CLI Intro
print("🎧 Spotify Voice Agent CLI")
print("Say 'dobby' to activate me. Then say a command like 'play Starboy'.")
print("Say 'stop' or 'exit' anytime to quit.\n")

# Initialize recognizer
recognizer = sr.Recognizer()

# Try to initialize mic
try:
    mic = sr.Microphone()
except OSError:
    print("❌ No microphone found. Plug one in maybe? 🤷‍♂️")
    exit()

# Function to wait for hotword ("dobby")
def wait_for_hotword(hotword="dobby"):
    while True:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            print("🧠 Waiting for 'dobby' to activate...")

            try:
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=3)
                trigger = recognizer.recognize_google(audio).lower().strip()
                print(f"🗣️ You said: {trigger}")
                if hotword in trigger:
                    print("🔓 Activated! Listening for your command...")
                    return True
                elif trigger in ['exit', 'stop', 'quit']:
                    print("👋 Exiting. Peace out!")
                    exit()
            except sr.UnknownValueError:
                print("🤷 Didn't catch that. Say 'dobby' to activate.")
            except sr.RequestError:
                print("🔌 Google Speech Recognition error.")
            except Exception as e:
                print(f"⚠️ Unexpected error: {e}")

# Function to listen for command after "dobby"
def listen_for_command():
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎤 Listening for command...")

        try:
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)
            command = recognizer.recognize_google(audio).lower().strip()
            print(f"🗣️ You said: {command}")
            return command
        except sr.UnknownValueError:
            print("🤷 Sorry, couldn't catch that.")
            return ""
        except sr.RequestError:
            print("🔌 Google Speech Recognition API is down.")
            return ""

# Main Loop: Wake word ➜ Command ➜ Repeat
while True:
    # Wait for user to say "dobby"
    if wait_for_hotword():
        # Once activated, listen for next actual command
        user_input = listen_for_command()

        # Handle exit if they say "stop" or "exit" after wake word
        if user_input in ['exit', 'quit', 'stop']:
            print("👋 Exiting. Stay vibey!")
            break

        # Send the voice command to backend
        try:
            response = requests.post(API_URL, json={"prompt": user_input})
            data = response.json()

            # Handle response from FastAPI
            if "response" in data:
                print("🎵", data["response"])
            elif "msg" in data:
                print("🎵", data["msg"])
            elif "error" in data:
                print("❌", data["error"])
            else:
                print("⚠️ Unexpected response:", data)

        # Handle backend/network issues
        except requests.exceptions.RequestException as e:
            print(f"🚫 Failed to reach backend: {e}")
        except json.JSONDecodeError:
            print("⚠️ Server response wasn't valid JSON.")

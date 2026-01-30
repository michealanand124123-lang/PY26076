import os
import json
import time
import subprocess
import platform
import asyncio
import tempfile
import speech_recognition as sr
import edge_tts
import requests
import re
import random
from pydub import AudioSegment
from pydub.playback import play
from datetime import datetime

# --- CONFIG ---
API_KEY = "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"
MODEL = "anthropic/claude-3-haiku"
VOICE = "en-US-GuyNeural"
HISTORY_FILE = "venom_chat_log.json"
MAX_HISTORY = 6

# --- Load previous chat context ---
def load_context():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)[-MAX_HISTORY:]
                messages = []
                for item in data:
                    messages.append({"role": "user", "content": f"{item['user']} (from earlier)"})
                    messages.append({"role": "assistant", "content": f"{item['venom']} (your earlier reply)"})
                return messages
        except Exception as e:
            print("⚠️ Failed to load chat history:", str(e))
    return []

# --- Save chat history to file ---
def save_to_json(user_text, venom_text):
    data = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
        except:
            pass
    data.append({
        "timestamp": str(datetime.now()),
        "user": user_text,
        "venom": venom_text
    })
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

# --- Get AI-generated reply from OpenRouter ---
def get_venom_reply(prompt, context_messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Add noise to avoid repeated responses
    noise = f"(time: {datetime.now().strftime('%H:%M:%S')}, rand: {random.randint(1, 9999)})"

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are 'Venom', a sarcastic multilingual Tamil-English AI assistant. Learn the user's tone and history. Speak with wit, sass, and roast. Keep replies short and funny."
            },
            *context_messages,
            {"role": "user", "content": f"{prompt} {noise}"}
        ]
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print("❌ API Error:", response.status_code, response.text)
    except Exception as e:
        print("❌ Request Failed:", str(e))
    return "Venom: Enna da error vandhuchu 🤦‍♂️!"

# --- Speak with robotic audio effect using pydub ---
def speak_text(text, print_before=True):
    async def _speak():
        try:
            if print_before:
                print("Venom:", text)

            temp_path = tempfile.mktemp(suffix=".mp3")
            communicate = edge_tts.Communicate(text, VOICE)
            await communicate.save(temp_path)

            # Load and apply robot effects
            sound = AudioSegment.from_file(temp_path, format="mp3")
            sound = sound._spawn(sound.raw_data, overrides={
                "frame_rate": int(sound.frame_rate * 0.85)
            }).set_frame_rate(44100)

            # Add echo
            delay_ms = 120
            echo = AudioSegment.silent(duration=delay_ms) + (sound - 8)
            combined = sound.overlay(echo)

            play(combined)
            os.remove(temp_path)
        except Exception as e:
            print("🛑 TTS Error:", str(e))

    asyncio.run(_speak())

# --- Capture voice from microphone ---
def take_voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Venom is listening... Speak now.")
        r.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=15)
            return r.recognize_google(audio)
        except:
            return ""

# --- Process a single query ---
def process_query(text):
    context = load_context()
    reply = get_venom_reply(text, context)

    # Remove stage directions like *laughs*
    cleaned_reply = re.sub(r"\*.*?\*", "", reply).strip()

    # Print and speak at the same time
    speak_text(cleaned_reply, print_before=True)

    # Save full reply
    save_to_json(text, reply)

    return reply

# --- Main loop ---
if __name__ == "__main__":
    print("🔥 Venom is starting...")
    print("🧠 Venom AI activated. Say or type something...")

    while True:
        print("\nSay or type 'Hey Venom' (or 'quit'):")
        user_input = input("You: ").strip().lower()
        if user_input == "quit":
            print("Venom: Bye! 🫡")
            break
        if user_input == "hey venom":
            user_input = take_voice_input()
            if not user_input:
                continue
        venom_reply = process_query(user_input)
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import re
import random
import requests
from datetime import datetime
import asyncio
import tempfile
import edge_tts
# from pydub import AudioSegment
# from pydub.playback import play

app = Flask(__name__)
CORS(app)

# --- CONFIG ---
API_KEY = "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"
MODEL = "anthropic/claude-3-haiku"
VOICE = "en-US-GuyNeural"
HISTORY_FILE = "infini_think_chat_log.json"
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
                    messages.append({"role": "assistant", "content": f"{item['infini_think']} (your earlier reply)"})
                return messages
        except Exception as e:
            print("[WARNING] Failed to load chat history:", str(e))
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
        "infini_think": venom_text
    })
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

# --- Get AI-generated reply from OpenRouter ---
def get_infini_think_reply(prompt, context_messages):
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
                "content": "You are 'Infini Think', a sarcastic multilingual Tamil-English AI assistant. Learn the user's tone and history. Speak with wit, sass, and roast. Keep replies short and funny."
            },
            *context_messages,
            {"role": "user", "content": f"{prompt} {noise}"}
        ]
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print("[ERROR] API Error:", response.status_code, response.text)
    except Exception as e:
        print("[ERROR] Request Failed:", str(e))
        # Mock response for testing UI
        responses = [
            "Enna solraan da? 😎",
            "Dei, edhuku innum pesara? 🙄",
            "Infini Think here! That's interesting... 🔥",
            "Aah, interesting indeed! Tell me more 👀",
            "Haha, nice one! 😆",
        ]
        return random.choice(responses)

# --- Process a single query ---
def process_query(text):
    context = load_context()
    reply = get_infini_think_reply(text, context)
    
    # Remove stage directions like *laughs*
    cleaned_reply = re.sub(r"\*.*?\*", "", reply).strip()
    
    # Save full reply
    save_to_json(text, reply)
    
    return cleaned_reply

# --- API Routes ---
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        reply = process_query(user_message)
        return jsonify({'reply': reply, 'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return jsonify({'history': data, 'success': True}), 200
        return jsonify({'history': [], 'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    try:
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("[*] Infini Think API Server starting on http://localhost:5000...")
    app.run(debug=False, port=5000, host='0.0.0.0')
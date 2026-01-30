from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import subprocess
import json
import threading
import requests
from datetime import datetime
import webbrowser

app = Flask(__name__)
CORS(app)

# Configuration
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "storage_path": r"C:\Users\KiTE\OneDrive\Desktop\html\data",
    "ollama_port": 11434,
    "model_name": "llama3",
    "ollama_url": "http://localhost:11434"
}

# Global state
CONFIG = DEFAULT_CONFIG.copy()
PHASE2_RUNNING = False
SYSTEM_PROMPT = ""

def load_config():
    global CONFIG
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            CONFIG.update(json.load(f))
    else:
        save_config()

def save_config():
    os.makedirs(os.path.dirname(CONFIG_FILE) or '.', exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(CONFIG, f, indent=2)

# ==================== PHASE 1: THE ENGINE ====================

@app.route('/api/phase1/status', methods=['GET'])
def phase1_status():
    try:
        response = requests.get(f"{CONFIG['ollama_url']}/api/tags", timeout=2)
        return jsonify({"running": response.status_code == 200})
    except:
        return jsonify({"running": False})

@app.route('/api/phase1/install', methods=['POST'])
def phase1_install():
    try:
        # Download Ollama installer
        result = subprocess.run(
            "powershell -Command \"(Invoke-WebRequest -Uri 'https://ollama.ai/download/OllamaSetup.exe' -OutFile 'OllamaSetup.exe'); Start-Process -FilePath 'OllamaSetup.exe' -Wait\"",
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        return jsonify({"message": "✅ Ollama installation started. Follow the installer."})
    except Exception as e:
        return jsonify({"message": f"⚠️ {str(e)}"})

@app.route('/api/phase1/download-model', methods=['POST'])
def phase1_download_model():
    try:
        # Pull Llama3 model
        subprocess.Popen([
            "ollama",
            "pull",
            CONFIG['model_name']
        ])
        return jsonify({"message": f"⏳ Downloading {CONFIG['model_name']}... This may take 10-45 minutes. You'll get a notification when done."})
    except Exception as e:
        return jsonify({"message": f"❌ Error: {str(e)}"})

@app.route('/api/phase1/ask', methods=['POST'])
def phase1_ask():
    data = request.json
    question = data.get('question', '')
    
    try:
        response = requests.post(
            f"{CONFIG['ollama_url']}/api/generate",
            json={
                "model": CONFIG['model_name'],
                "prompt": question,
                "stream": False
            },
            timeout=120
        )
        result = response.json()
        return jsonify({"answer": result.get('response', 'No response')})
    except Exception as e:
        return jsonify({"error": str(e)})

# ==================== PHASE 2: THE SHIELDS ====================

@app.route('/api/phase2/start', methods=['POST'])
def phase2_start():
    global PHASE2_RUNNING
    PHASE2_RUNNING = True
    
    # Start mouse jitter in background
    threading.Thread(target=mouse_jitter_loop, daemon=True).start()
    # Start search decoy in background
    threading.Thread(target=search_decoy_loop, daemon=True).start()
    
    return jsonify({"status": "shields activated"})

@app.route('/api/phase2/stop', methods=['POST'])
def phase2_stop():
    global PHASE2_RUNNING
    PHASE2_RUNNING = False
    return jsonify({"status": "shields deactivated"})

@app.route('/api/phase2/config', methods=['POST'])
def phase2_config():
    data = request.json
    config = {
        "jitter_pixels": data.get('jitter_pixels', 1),
        "jitter_interval": data.get('jitter_interval', 30),
        "decoy_queries": data.get('decoy_queries', [])
    }
    
    with open("phase2_config.json", 'w') as f:
        json.dump(config, f)
    
    return jsonify({"message": "Configuration saved"})

def mouse_jitter_loop():
    try:
        import pyautogui
        import time
        import random
        
        config = json.load(open("phase2_config.json")) if os.path.exists("phase2_config.json") else {"jitter_pixels": 1, "jitter_interval": 30}
        
        while PHASE2_RUNNING:
            x, y = pyautogui.position()
            offset_x = random.randint(-config['jitter_pixels'], config['jitter_pixels'])
            offset_y = random.randint(-config['jitter_pixels'], config['jitter_pixels'])
            pyautogui.moveTo(x + offset_x, y + offset_y, duration=0.1)
            time.sleep(config['jitter_interval'])
    except:
        pass

def search_decoy_loop():
    try:
        import webbrowser
        import time
        import random
        
        config = json.load(open("phase2_config.json")) if os.path.exists("phase2_config.json") else {"decoy_queries": ["how to grow tomatoes"]}
        queries = config.get('decoy_queries', ["how to grow tomatoes"])
        
        while PHASE2_RUNNING:
            query = random.choice(queries)
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            try:
                webbrowser.open(url)
            except:
                pass
            time.sleep(random.randint(300, 900))  # 5-15 minutes
    except:
        pass

# ==================== PHASE 3: THE BRAIN UPGRADES ====================

@app.route('/api/phase3/explain', methods=['POST'])
def phase3_explain():
    data = request.json
    content = data.get('content', '')
    style = data.get('style', 'simple')
    
    styles = {
        'starwars': "Explain this using Star Wars analogies and references. Be creative and fun.",
        'simple': "Explain this in the simplest way possible for a 10-year-old to understand.",
        'technical': "Provide a detailed, technical explanation with proper terminology.",
        'comic': "Explain this as if it's a comic book story with heroes and villains."
    }
    
    system_prompt = SYSTEM_PROMPT or styles.get(style, styles['simple'])
    
    try:
        response = requests.post(
            f"{CONFIG['ollama_url']}/api/generate",
            json={
                "model": CONFIG['model_name'],
                "prompt": f"{system_prompt}\n\n{content}",
                "stream": False
            },
            timeout=120
        )
        result = response.json()
        return jsonify({"explanation": result.get('response', 'No response')})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/phase3/config', methods=['POST'])
def phase3_config():
    global SYSTEM_PROMPT
    data = request.json
    SYSTEM_PROMPT = data.get('system_prompt', '')
    
    with open("phase3_prompt.txt", 'w') as f:
        f.write(SYSTEM_PROMPT)
    
    return jsonify({"message": "Settings saved"})

# ==================== PHASE 4: THE CONTROL PANEL ====================

@app.route('/api/phase4/self-destruct', methods=['POST'])
def phase4_self_destruct():
    try:
        import shutil
        data_path = CONFIG.get('storage_path', r'C:\Users\KiTE\OneDrive\Desktop\html\data')
        
        if os.path.exists(data_path):
            shutil.rmtree(data_path)
        
        # Clear logs
        for file in ['phase2_config.json', 'phase3_prompt.txt', 'config.json']:
            if os.path.exists(file):
                os.remove(file)
        
        return jsonify({"message": "All local data has been deleted. System clean."})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        global CONFIG
        data = request.json
        CONFIG.update(data)
        save_config()
        return jsonify({"message": "Settings saved"})
    return jsonify(CONFIG)

# ==================== STARTUP ====================

@app.route('/', methods=['GET'])
def root():
    return "AI Control Panel Backend Running"

if __name__ == '__main__':
    load_config()
    
    # Create data directory
    os.makedirs(CONFIG['storage_path'], exist_ok=True)
    
    print("🚀 Starting AI Control Panel Backend...")
    print(f"📍 Local URL: http://localhost:5000")
    
    # Open browser
    threading.Thread(target=lambda: webbrowser.open('http://localhost:5000'), daemon=True).start()
    
    app.run(debug=False, host='localhost', port=5000)
#!/usr/bin/env python
import os
import sys

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Import after changing directory
from app import app

if __name__ == '__main__':
    try:
        print("[*] Starting Infini Think API Server...")
        print("[*] Server will be available at http://localhost:5000")
        print("[*] Press Ctrl+C to stop the server\n")
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n[*] Server stopped")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        sys.exit(1)

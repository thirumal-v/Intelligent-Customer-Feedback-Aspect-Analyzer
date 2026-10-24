"""
Launcher for Intelligent Customer Feedback & Aspect Analyzer.
"""

import sys
import webbrowser
import threading
import time
from app import app

def open_browser():
    time.sleep(1.5)
    url = "http://127.0.0.1:5000"
    print(f"\n[Browser] Opening {url} ...\n")
    webbrowser.open(url)

if __name__ == "__main__":
    print("=" * 65)
    print("  AspectPulse AI: Intelligent Customer Feedback & Aspect Analyzer")
    print("  Transformers Engine: Hugging Face DistilBERT (PyTorch)")
    print("  Local URL: http://127.0.0.1:5000")
    print("=" * 65)

    # Automatically open web browser in background
    threading.Thread(target=open_browser, daemon=True).start()

    app.run(host="127.0.0.1", port=5000, debug=False)

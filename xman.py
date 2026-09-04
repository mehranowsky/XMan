import json
import sys
import re
import urllib.request
import urllib.error
import winsound  # <--- Still use winsound, but with MessageBeep

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5-coder:0.5b"

def ask_ollama(prompt):
    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }).encode('utf-8')
    
    req = urllib.request.Request(OLLAMA_URL, data=payload, method='POST')
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result["response"]
    except urllib.error.URLError:
        return "ERROR: Ollama is not running! Start it with 'ollama serve'."

def extract_all_code_blocks(text):
    pattern = r'```(?:\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    return [block.strip() for block in matches if block.strip()]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python xman.py \"Your instruction here\"")
        sys.exit(1)
    
    prompt = " ".join(sys.argv[1:])
    
    print(f"🧠 Generating code... (this may take 10-30 seconds)\n")
    response = ask_ollama(prompt)
    
    # 🔔 BEEP! Plays through your speakers/headphones (NOT the motherboard beeper)
    winsound.MessageBeep()
    
    code_blocks = extract_all_code_blocks(response)
    
    if not code_blocks:        
        print("📝 AI Response was:\n", response)
        sys.exit(0)
    
    print(f"✅ Found {len(code_blocks)} code block(s).")
    
    base = input("📁 Enter base filename (e.g., 'app'): ").strip()
    if not base:
        base = "code"
    
    ext = input("📁 Enter file extension (default: py): ").strip()
    if not ext:
        ext = "py"
    if ext.startswith('.'):
        ext = ext[1:]
    
    saved_count = 0
    for i, code in enumerate(code_blocks, 1):
        filename = f"{base}_{i}.{ext}"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"   ✅ Saved: {filename}")
        saved_count += 1
    
    # 🔔 Second beep to confirm saving is done
    winsound.MessageBeep()
    print(f"\n🎉 Done! Saved {saved_count} pure-code file(s).")
import json
import sys
import re
import urllib.request
import urllib.error

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

def extract_code(text):
    """Extract code from markdown blocks (```python ... ```)"""
    # Look for code blocks
    pattern = r'```(?:python)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    if matches:
        # Return the code inside the blocks
        return "\n\n".join(matches).strip()
    else:
        # If no markdown, return the whole text (maybe it's just raw code)
        return text.strip()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python xman.py \"Your instruction here\"")
        sys.exit(1)
    
    prompt = " ".join(sys.argv[1:])
    
    print(f"🧠 Thinking...\n")
    response = ask_ollama(prompt)
    
    if "ERROR" in response:
        print(response)
        sys.exit(1)
    
    # 1. Show the AI's full response (so you see the explanation)
    print("=" * 50)
    print("🤖 AI RESPONSE:")
    print("=" * 50)
    print(response)
    print("=" * 50)
    
    # 2. Extract only the code
    code_only = extract_code(response)
    
    if not code_only:
        print("ℹ️ No code detected in the response. Nothing to save.")
        sys.exit(0)
    
    # 3. Ask if they want to save the extracted code
    print("\n📄 Extracted Code Preview:")
    print("-" * 40)
    print(code_only[:500] + ("..." if len(code_only) > 500 else ""))
    print("-" * 40)
    
    save_choice = input("💾 Save this code to a file? (Enter filename, or press Enter to skip): ").strip()
    
    if save_choice:
        with open(save_choice, "w", encoding="utf-8") as f:
            f.write(code_only)
        print(f"✅ Code saved to: {save_choice}")
    else:
        print("❌ File not saved.")
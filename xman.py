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

def extract_all_code_blocks(text):
    """Extract all code blocks (```...```) from the text"""
    # This finds everything between ``` and ```
    pattern = r'```(?:\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    # Clean up trailing/leading whitespace
    return [block.strip() for block in matches if block.strip()]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python xman.py \"Your instruction here\"")
        sys.exit(1)
    
    prompt = " ".join(sys.argv[1:])
    
    print(f"🧠 Thinking... (this may take 10-30 seconds)\n")
    response = ask_ollama(prompt)
    
    if "ERROR" in response:
        print(response)
        sys.exit(1)
    
    # 1. Show the AI's full response
    print("=" * 60)
    print("🤖 AI RESPONSE:")
    print("=" * 60)
    print(response)
    print("=" * 60)
    
    # 2. Extract ALL code blocks
    code_blocks = extract_all_code_blocks(response)
    
    if not code_blocks:
        print("ℹ️ No code blocks detected. Nothing to save.")
        sys.exit(0)
    
    print(f"\n📦 Found {len(code_blocks)} code block(s) in the response.\n")
    
    # 3. Loop through each block and ask for a filename
    saved_count = 0
    for i, block in enumerate(code_blocks, 1):
        print(f"--- Block #{i} Preview ---")
        # Show first 200 chars of the block so they know what it is
        preview = block[:200] + ("..." if len(block) > 200 else "")
        print(preview)
        print("-------------------------")
        
        # Ask what to name this specific file
        filename = input(f"💾 Enter filename for Block #{i} (or press Enter to skip): ").strip()
        
        if filename:
            # Check if it has an extension, if not, add .py
            if '.' not in filename:
                filename += '.py'
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(block)
            print(f"   ✅ Saved to: {filename}\n")
            saved_count += 1
        else:
            print(f"   ⏭️ Skipped Block #{i}\n")
    
    if saved_count == 0:
        print("❌ No files were saved.")
    else:
        print(f"🎉 Done! Saved {saved_count} file(s).")
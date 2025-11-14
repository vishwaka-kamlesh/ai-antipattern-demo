import os
import json
import requests
import sys

MODEL = "meta-llama/Llama-3.1-8B-Instruct"
API_URL = "https://router.huggingface.co/v1/chat/completions"

token = os.getenv("HF_API_TOKEN")
if not token:
    print("❌ Missing HF_API_TOKEN")
    sys.exit(1)

print("📂 Reading Semgrep results...")

try:
    data = json.load(open("results.json", "r"))
except Exception:
    print("✨ No issues or invalid results.json")
    open("ai_output.json", "w").write("[]")
    sys.exit(0)

issues = data.get("results", [])
if not issues:
    print("🧼 Clean diff, no issues.")
    open("ai_output.json", "w").write("[]")
    sys.exit(0)

print(f"🔍 Sending {len(issues)} issues to AI...")

prompt = f"""
Convert the following Semgrep issues into a pure JSON array.

STRICT OUTPUT RULES:
1️⃣ Output ONLY a JSON array: [ {...}, {...} ]
2️⃣ No markdown, no code blocks, no narration.
3️⃣ No trailing commas.
4️⃣ Use only double quotes for strings.
5️⃣ Every element MUST include EXACTLY these fields:
   - "file": string
   - "line": number
   - "issue": string
   - "severity": string
   - "explanation": string
   - "detailed_fix": string
   - "code_patch": string
   - "risk": string
6️⃣ If information is missing, fill with a brief helpful message.
7️⃣ The output will be parsed by a machine. Any deviation breaks the workflow.

Now transform this Semgrep JSON (DO NOT reformat or include its keys):
{json.dumps(issues, indent=2)}
"""

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "You are a precise and disciplined code reviewer. Output must be valid JSON only."},
        {"role": "user", "content": prompt},
    ],
    "temperature": 0.0,
    "max_tokens": 1000,
}

resp = requests.post(API_URL,
                     headers={"Authorization": f"Bearer {token}"},
                     json=payload, timeout=60)

if resp.status_code != 200:
    print("❌ API Error:", resp.text)
    open("ai_output.json", "w").write("[]")
    sys.exit(1)

content = resp.json()["choices"][0]["message"]["content"].strip()

if content.startswith("```"):
    content = content.replace("```", "").replace("json", "").strip()

try:
    parsed = json.loads(content)
except Exception:
    print("⚠️ AI did not return valid JSON. Saving empty array.")
    parsed = []

json.dump(parsed, open("ai_output.json", "w"), indent=2)
print("💾 Saved ai_output.json")

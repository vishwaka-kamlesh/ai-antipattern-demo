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
Analyze Semgrep issues and convert them into a JSON array.

Each element must include:
- file
- line
- issue
- severity
- explanation(why fixing this matters?)
- detailed_fix
- code_patch
- risk

Rules:
• Return ONLY valid JSON
• No markdown
• No comments
• No surrounding text

Semgrep issues:
{json.dumps(issues)}
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

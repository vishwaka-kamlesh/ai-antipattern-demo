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
    print("✨ No issues or invalid Semgrep output.")
    json.dump([], open("ai_output.json", "w"), indent=2)
    sys.exit(0)

issues = data.get("results", [])
if not issues:
    print("🧼 Clean diff, no issues.")
    json.dump([], open("ai_output.json", "w"), indent=2)
    sys.exit(0)

print(f"🔍 Sending {len(issues)} issues to AI...")

prompt = f"""
Convert these Semgrep issues into a JSON array.

STRICT RULES:
• Return ONLY a JSON array: [{{}}, {{}}]
• No markdown, no text outside JSON
• Every element MUST contain:
  "file", "line", "issue", "severity", "explanation",
  "detailed_fix", "code_patch", "risk"

Use the field "code" to generate a corrected code_patch.

Semgrep issues:
{json.dumps(issues, indent=2)}
"""

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "You are a strict senior backend code reviewer. Output only JSON."},
        {"role": "user", "content": prompt},
    ],
    "temperature": 0.0,
    "max_tokens": 1200
}

resp = requests.post(API_URL,
    headers={"Authorization": f"Bearer {token}"},
    json=payload,
    timeout=60
)

if resp.status_code != 200:
    print(f"❌ API Error: {resp.text}")
    json.dump([], open("ai_output.json", "w"), indent=2)
    sys.exit(1)

content = resp.json()["choices"][0]["message"]["content"]
content = content.replace("```json", "").replace("```", "").strip()

try:
    parsed = json.loads(content)
except json.JSONDecodeError:
    print("⚠️ AI output is not strict JSON. Attempting fallback parse...")
    parsed = []

json.dump(parsed, open("ai_output.json", "w"), indent=2)
print("💾 Saved ai_output.json")

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
    content = open("results.json", "r", encoding="utf-8").read().strip()
    if not content:
        raise Exception("Empty content")
    data = json.loads(content)
except Exception:
    print("✨ No issues or invalid Semgrep output.")
    open("ai_output.json", "w").write("[]")
    sys.exit(0)

issues = data.get("results", [])
if not issues:
    print("🧼 Clean diff, no issues.")
    open("ai_output.json", "w").write("[]")
    sys.exit(0)

print(f"🔍 Sending {len(issues)} issues to AI...")

prompt = f"""
You are a senior code reviewer.
Convert issues into JSON array with:

file, line, issue, severity, explanation,
detailed_fix, code_patch, risk

Return ONLY JSON array!

Semgrep issues:
{json.dumps(issues)}
"""

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "You are an expert code reviewer."},
        {"role": "user", "content": prompt},
    ],
    "temperature": 0.0,
}

resp = requests.post(API_URL,
    headers={"Authorization": f"Bearer {token}"},
    json=payload, timeout=60
)

if resp.status_code != 200:
    print("❌ API Error:", resp.text)
    open("ai_output.json", "w").write("[]")
    sys.exit(1)

content = resp.json()["choices"][0]["message"]["content"]

clean = content.strip().strip("```json").strip("```").strip()
clean = clean.replace("\\\"", "\"")

try:
    parsed = json.loads(clean)
except:
    print("⚠️ AI output was not valid JSON, ignoring.")
    parsed = []

json.dump(parsed, open("ai_output.json","w"), indent=2)
print("💾 Saved ai_output.json")

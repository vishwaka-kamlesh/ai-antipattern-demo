import os
import json
import requests
import sys

MODEL = "meta-llama/Llama-3.1-8B-Instruct"          # ✅ live model slug
API_URL = "https://router.huggingface.co/v1/chat/completions"  # ✅ modern endpoint

token = os.getenv("HF_API_TOKEN")
if not token:
    print("❌ Missing HF_API_TOKEN environment variable.")
    sys.exit(1)

if not os.path.exists("results.json"):
    print("❌ Missing results.json from Semgrep.")
    sys.exit(1)

with open("results.json", "r") as f:
    data = json.load(f)

if not data.get("results"):
    print("✅ No issues found. Nothing to send to Hugging Face.")
    sys.exit(0)

prompt = f"""
You are a senior developer reviewing code issues found by Semgrep.
For each issue, explain what is wrong and how to fix it.
Respond as JSON:
[
  {{
    "file": "string",
    "line": number,
    "issue": "string",
    "fix": "string"
  }}
]
Here are the issues:
{json.dumps(data['results'], indent=2)}
"""

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "You are an expert code reviewer."},
        {"role": "user", "content": prompt},
    ],
    "max_tokens": 500,
}

resp = requests.post(
    API_URL,
    headers={"Authorization": f"Bearer {token}"},
    json=payload,
)

if resp.status_code != 200:
    print(f"❌ Hugging Face API error: {resp.status_code}")
    print(resp.text)
    sys.exit(1)

print("✅ Response received from Hugging Face.")

with open("ai_output.json", "w", encoding="utf-8") as f:
    json.dump(resp.json(), f, indent=2, ensure_ascii=False)

print("🧠 AI analysis saved to ai_output.json")

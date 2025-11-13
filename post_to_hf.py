import os, json, requests, sys

MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"
token = os.getenv("HF_API_TOKEN")

if not token:
    print("❌ Missing HF_API_TOKEN environment variable.")
    sys.exit(1)

if not os.path.exists("results.json"):
    print("❌ Missing results.json from Semgrep.")
    sys.exit(1)

with open("results.json") as f:
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

resp = requests.post(
    f"https://api-inference.huggingface.co/models/{MODEL}",
    headers={"Authorization": f"Bearer {token}"},
    json={"inputs": prompt, "parameters": {"max_new_tokens": 300}},
)

if resp.status_code != 200:
    print(f"❌ Hugging Face API error: {resp.status_code}")
    print(resp.text)
    sys.exit(1)

print("✅ Response received from Hugging Face.")
with open("ai_output.json", "w") as f:
    f.write(json.dumps(resp.json(), indent=2))

import os, json, requests, sys

MODEL = "meta-llama/Llama-3.1-8B-Instruct"
API_URL = "https://router.huggingface.co/v1/chat/completions"

token = os.getenv("HF_API_TOKEN")
if not token:
    print("❌ Missing HF_API_TOKEN")
    sys.exit(1)

if not os.path.exists("results.json"):
    print("❌ Missing results.json from Semgrep.")
    sys.exit(1)

print("📂 Reading Semgrep results...")
data = json.load(open("results.json", "r"))

issues = data.get("results", [])
if not issues:
    print("✨ No issues found. Creating empty analysis file.")
    open("ai_output.json", "w").write("[]")
    sys.exit(0)

prompt = f"""
You are a senior backend code reviewer.
Convert the Semgrep issues into a friendlier structure.

Return ONLY a JSON array. Each item must have:
- file
- line
- issue
- severity (Critical|High|Medium|Low)
- explanation
- detailed_fix
- code_patch (short example)
- risk

Here are the issues:
{json.dumps(issues)}
"""

payload = {
    "model": MODEL,
    "messages": [{"role": "user", "content": prompt}],
    "temperature": 0.0,
}

print("🤖 Contacting Hugging Face...")
resp = requests.post(
    API_URL,
    headers={"Authorization": f"Bearer {token}"},
    json=payload,
    timeout=60
)

if resp.status_code != 200:
    print("❌ API Error:", resp.text)
    sys.exit(1)

content = resp.json()["choices"][0]["message"]["content"]

# Fix JSON escaping issues
clean = content.strip().strip("```json").strip("```")
clean = clean.replace("\\\"", "\"")

try:
    parsed = json.loads(clean)
except:
    print("⚠️ AI output not strict JSON, falling back to raw")
    parsed = []

with open("ai_output.json", "w", encoding="utf-8") as f:
    json.dump(parsed, f, indent=2, ensure_ascii=False)

print("💾 ai_output.json generated successfully")

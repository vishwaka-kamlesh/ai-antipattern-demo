import os
import json
import requests
import sys

# --------------------------------------------------------------------
#  CONFIG
# --------------------------------------------------------------------
MODEL = "meta-llama/Llama-3.1-8B-Instruct"
API_URL = "https://router.huggingface.co/v1/chat/completions"

token = os.getenv("HF_API_TOKEN")
if not token:
    print("❌ Missing HF_API_TOKEN")
    sys.exit(1)

# --------------------------------------------------------------------
#  LOAD SEMGREP RESULTS SAFELY
# --------------------------------------------------------------------
print("📂 Reading Semgrep results...")

if not os.path.exists("results.json"):
    print("✨ No Semgrep output found. Assuming no issues.")
    open("ai_output.json", "w").write("[]")
    sys.exit(0)

try:
    raw = open("results.json", "r", encoding="utf-8").read().strip()
    if not raw:
        print("✨ Semgrep results empty. No issues detected.")
        open("ai_output.json", "w").write("[]")
        sys.exit(0)
    data = json.loads(raw)
except Exception as e:
    print(f"⚠️ Failed to parse Semgrep output: {e}")
    open("ai_output.json", "w").write("[]")
    sys.exit(0)

issues = data.get("results", [])
if not issues:
    print("🧼 Clean diff. No anti-patterns detected.")
    open("ai_output.json", "w").write("[]")
    sys.exit(0)

print(f"🔍 Found {len(issues)} issues. Sending to AI for review...")

# --------------------------------------------------------------------
#  BUILD PROMPT FOR POLISHED REVIEW
# --------------------------------------------------------------------
prompt = f"""
You are a senior code reviewer. Analyze the following Semgrep results
and convert them into a clean JSON array for developers.

Each issue must include:
- file
- line
- issue (concise)
- severity (Critical|High|Medium|Low)
- explanation (developer-friendly summary)
- detailed_fix (actionable fix steps)
- code_patch (small example patch)
- risk (what happens if ignored)

Return ONLY the JSON array, no text outside JSON.

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

# --------------------------------------------------------------------
#  CALL HUGGING FACE AI
# --------------------------------------------------------------------
print("🤖 Contacting Hugging Face...")
try:
    resp = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
        timeout=60
    )
except Exception as e:
    print("❌ Request failed:", e)
    open("ai_output.json", "w").write("[]")
    sys.exit(1)

if resp.status_code != 200:
    print(f"❌ API Error {resp.status_code}: {resp.text}")
    open("ai_output.json", "w").write("[]")
    sys.exit(1)

content = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")

# --------------------------------------------------------------------
#  CLEAN MODEL OUTPUT TO VALID JSON
# --------------------------------------------------------------------
clean = content.strip().strip("```json").strip("```").strip()
clean = clean.replace("\\\"", "\"")

try:
    parsed = json.loads(clean)
except Exception:
    print("⚠️ AI response not valid JSON. Storing empty result.")
    parsed = []

# --------------------------------------------------------------------
#  SAVE CLEAN JSON OUTPUT
# --------------------------------------------------------------------
with open("ai_output.json", "w", encoding="utf-8") as f:
    json.dump(parsed, f, indent=2, ensure_ascii=False)

print("💾 Saved AI analysis → ai_output.json")
print("✨ Done")

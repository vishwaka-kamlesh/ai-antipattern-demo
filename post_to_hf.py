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
    print("❌ Missing HF_API_TOKEN environment variable.")
    sys.exit(1)

# --------------------------------------------------------------------
#  LOAD SEMGREP RESULTS
# --------------------------------------------------------------------
if not os.path.exists("results.json"):
    print("❌ Missing results.json from Semgrep.")
    sys.exit(1)

with open("results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

if not data or "results" not in data:
    print("✅ No issues found. Skipping AI analysis.")
    sys.exit(0)

# --------------------------------------------------------------------
#  FILTER SIGNIFICANT ISSUES (ERROR / WARNING)
# --------------------------------------------------------------------
bad_issues = [
    r for r in data["results"]
    if r.get("extra", {}).get("severity", "").upper() in ("ERROR", "WARNING")
]

if not bad_issues:
    print("✅ Only minor or informational issues found. Skipping AI analysis.")
    sys.exit(0)

print(f"🔍 Found {len(bad_issues)} significant issues — triggering AI review.")

# Use only filtered issues for AI
data["results"] = bad_issues

# --------------------------------------------------------------------
#  BUILD PROMPT FOR DETAILED REVIEW
# --------------------------------------------------------------------
detailed_instruction = """
You are a senior backend engineer and code reviewer.
Analyze each issue reported by Semgrep below and produce a detailed corrective plan.
Return a valid JSON array. Each element must contain:

- file (string): file path
- line (number): approximate line number
- issue (string): short issue summary
- severity (string): Critical|High|Medium|Low
- explanation (string): reason for the problem
- detailed_fix (string): multi-step remediation plan with rationale
- code_patch (string|null): small concrete code example or patch
- tests (string|null): how to verify the fix
- risk (string): possible side effects
- references (array[string]): 0–3 authoritative links or keywords

Be concise but thorough. Output ONLY valid JSON.
"""

prompt = f"""
{detailed_instruction}

Semgrep results (JSON):
{json.dumps(data['results'], indent=2)}

Return only the JSON array.
"""

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "You are an expert code reviewer. Be precise, detailed, and conservative."},
        {"role": "user", "content": prompt},
    ],
    "temperature": 0.0,
    "max_tokens": 1200,
}

# --------------------------------------------------------------------
#  CALL HUGGING FACE CHAT COMPLETIONS API
# --------------------------------------------------------------------
print("⚙️  Sending request to Hugging Face…")
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

# --------------------------------------------------------------------
#  SAVE AI RESULT
# --------------------------------------------------------------------
result_json = resp.json()
content = result_json.get("choices", [{}])[0].get("message", {}).get("content", "")

try:
    parsed = json.loads(content)
except Exception:
    print("⚠️  Model output not strict JSON; saving raw content instead.")
    parsed = content

output_path = "ai_output.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(parsed, f, indent=2, ensure_ascii=False)

print(f"🧠 AI detailed analysis saved to {output_path}")

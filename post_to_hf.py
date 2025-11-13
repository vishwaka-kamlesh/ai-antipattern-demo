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

print("📂 Loading results.json...")
with open("results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"📊 Raw data keys: {data.keys()}")
print(f"📊 Total results: {len(data.get('results', []))}")

if not data or "results" not in data:
    print("❌ No results key found in Semgrep output.")
    sys.exit(1)

if len(data["results"]) == 0:
    print("✅ No issues found. Skipping AI analysis.")
    sys.exit(0)

# --------------------------------------------------------------------
#  FILTER SIGNIFICANT ISSUES (ERROR / WARNING)
# --------------------------------------------------------------------
print("🔍 Filtering for ERROR/WARNING severity issues...")
bad_issues = []

for r in data["results"]:
    severity = r.get("extra", {}).get("severity", "").upper()
    print(f"  - Issue: {r.get('check_id')} | Severity: {severity}")
    if severity in ("ERROR", "WARNING"):
        bad_issues.append(r)

print(f"📋 Filtered {len(bad_issues)} significant issues out of {len(data['results'])} total")

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
    "max_tokens": 2000,  # Increased for more detailed responses
}

# --------------------------------------------------------------------
#  CALL HUGGING FACE CHAT COMPLETIONS API
# --------------------------------------------------------------------
print("⚙️  Sending request to Hugging Face…")
try:
    resp = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
        timeout=60
    )
    
    print(f"📡 Response status: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"❌ Hugging Face API error: {resp.status_code}")
        print(f"Response: {resp.text}")
        sys.exit(1)
    
    print("✅ Response received from Hugging Face.")
    
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")
    sys.exit(1)

# --------------------------------------------------------------------
#  SAVE AI RESULT
# --------------------------------------------------------------------
result_json = resp.json()
print(f"📦 Response keys: {result_json.keys()}")

content = result_json.get("choices", [{}])[0].get("message", {}).get("content", "")
print(f"📝 Content length: {len(content)} characters")
print(f"📝 Content preview: {content[:200]}...")

try:
    # Try to parse as JSON
    parsed = json.loads(content)
    print(f"✅ Successfully parsed AI output as JSON ({len(parsed)} items)")
except Exception as e:
    print(f"⚠️  Model output not strict JSON: {e}")
    print("💾 Saving raw content instead.")
    parsed = content

output_path = "ai_output.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(parsed, f, indent=2, ensure_ascii=False)

print(f"🧠 AI detailed analysis saved to {output_path}")
print(f"✅ Script completed successfully")
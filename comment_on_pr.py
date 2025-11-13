import os
import json
from github import Github

# --- Get PR context ---
repo_name = os.getenv("GITHUB_REPOSITORY")
ref = os.getenv("GITHUB_REF", "")
pr_number = int(os.getenv("PR_NUMBER") or (ref.split("/")[-1] if "pull" in ref else 0))

gh = Github(os.getenv("GITHUB_TOKEN"))
repo = gh.get_repo(repo_name)
pr = repo.get_pull(pr_number)

# --- Load AI output ---
with open("ai_output.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

# Extract message content if using chat completion
if isinstance(raw, dict) and raw.get("choices"):
    content = raw["choices"][0]["message"]["content"]
else:
    content = json.dumps(raw, indent=2)

# Try parsing the JSON array produced by the model
try:
    issues = json.loads(content)
except Exception:
    # If parsing fails, post raw text so you can debug
    issues = [{"file": "N/A", "issue": "AI output not valid JSON", "details": content}]

# --- Build the comment body ---
body_lines = ["### 🤖 AI Detailed Anti-Pattern Review\n"]
for it in issues:
    body_lines.append(f"**File:** {it.get('file','?')} (line {it.get('line','?')})")
    body_lines.append(f"**Issue:** {it.get('issue','?')}")
    if it.get("severity"):
        body_lines.append(f"**Severity:** {it.get('severity')}")
    if it.get("explanation"):
        body_lines.append(f"**Explanation:** {it.get('explanation')}")
    if it.get("detailed_fix"):
        body_lines.append(f"**Detailed Fix:**\n{it.get('detailed_fix')}")
    if it.get("code_patch"):
        body_lines.append("**Suggested Code Patch:**\n```")
        body_lines.append(it.get("code_patch"))
        body_lines.append("```")
    if it.get("tests"):
        body_lines.append(f"**Tests:**\n{it.get('tests')}")
    if it.get("risk"):
        body_lines.append(f"**Risk:**\n{it.get('risk')}")
    if it.get("references"):
        refs = "\n".join(f"- {r}" for r in it.get("references"))
        body_lines.append(f"**References:**\n{refs}")
    body_lines.append("---")

comment_body = "\n".join(body_lines)

# --- Post the comment on the PR ---
pr.create_issue_comment(comment_body)
print("✅ Posted AI detailed report to PR")

import os
import json
from github import Github

# --------------------------------------------------------------------
#  DETECT PR CONTEXT
# --------------------------------------------------------------------
repo_name = os.getenv("GITHUB_REPOSITORY")
ref = os.getenv("GITHUB_REF", "")
pr_number = os.getenv("PR_NUMBER")

if not pr_number:
    if "refs/pull/" in ref:
        try:
            pr_number = ref.split("/")[2]
        except IndexError:
            pr_number = None

if not pr_number:
    raise ValueError("❌ Unable to determine pull request number from environment variables.")

pr_number = int(pr_number)

# --------------------------------------------------------------------
#  CONNECT TO GITHUB
# --------------------------------------------------------------------
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise ValueError("❌ Missing GITHUB_TOKEN environment variable.")

gh = Github(token)
repo = gh.get_repo(repo_name)
pr = repo.get_pull(pr_number)

# --------------------------------------------------------------------
#  LOAD AI OUTPUT
# --------------------------------------------------------------------
if not os.path.exists("ai_output.json"):
    raise FileNotFoundError("❌ ai_output.json not found — ensure post_to_hf.py ran successfully.")

with open("ai_output.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

if isinstance(raw, dict) and raw.get("choices"):
    content = raw["choices"][0]["message"]["content"]
else:
    content = json.dumps(raw, indent=2)

try:
    issues = json.loads(content)
except Exception:
    issues = [{"file": "N/A", "issue": "AI output not valid JSON", "details": content}]

# --------------------------------------------------------------------
#  BUILD MARKDOWN COMMENT
# --------------------------------------------------------------------
body_lines = ["### 🤖 AI Detailed Anti-Pattern Review\n"]

for it in issues:
    file = it.get("file", "?")
    line = it.get("line", "?")
    issue = it.get("issue", "")
    severity = it.get("severity", "")
    explanation = it.get("explanation", "")
    detailed_fix = it.get("detailed_fix", "")
    code_patch = it.get("code_patch", "")
    tests = it.get("tests", "")
    risk = it.get("risk", "")
    refs = it.get("references", [])

    body_lines.append(f"**File:** `{file}` (line {line})")
    if severity:
        body_lines.append(f"**Severity:** {severity}")
    if issue:
        body_lines.append(f"**Issue:** {issue}")
    if explanation:
        body_lines.append(f"**Explanation:** {explanation}")
    if detailed_fix:
        body_lines.append(f"**Detailed Fix:**\n{detailed_fix}")
    if code_patch:
        body_lines.append("**Suggested Code Patch:**\n```")
        body_lines.append(code_patch)
        body_lines.append("```")
    if tests:
        body_lines.append(f"**Suggested Tests:**\n{tests}")
    if risk:
        body_lines.append(f"**Risk:**\n{risk}")
    if refs:
        body_lines.append("**References:**")
        for r in refs:
            body_lines.append(f"- {r}")
    body_lines.append("---")

comment_body = "\n".join(body_lines)

# --------------------------------------------------------------------
#  POST COMMENT TO PR
# --------------------------------------------------------------------
pr.create_issue_comment(comment_body)
print("✅ Posted AI detailed anti-pattern report to PR.")

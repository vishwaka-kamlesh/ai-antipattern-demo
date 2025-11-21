import os
import json
from github import Github, Auth

SASSY_RULE_GUIDE = {
    "empty-catch-block": {
        "why": "Swallowed exceptions hide debugging clues and corrupt flows.",
        "fix": "log or rethrow the exception.",
        "roast": "Pretending problems don’t exist is not engineering."
    },
    "no-print-stacktrace": {
        "why": "printStackTrace logs without structure and leaks details.",
        "fix": 'logger.error("Unexpected error", e)',
        "roast": "Your console is not Splunk, buddy."
    },
    "no-system-out": {
        "why": "System.out bypasses log management and destroys observability.",
        "fix": 'logger.info("message")',
        "roast": "First-year Java class called. It wants its println back."
    },
    # ... keep your other rules exactly same but add a "why" field to each ...
}

token = os.getenv("GITHUB_TOKEN")
repo_name = os.getenv("GITHUB_REPOSITORY")
pr_number = os.getenv("PR_NUMBER")

if not token or not repo_name or not pr_number:
    print("❌ Missing required environment variables")
    exit(1)

try:
    data = json.load(open("results.json"))
except:
    print("⚠️ No results.json found.")
    exit(0)

issues = data.get("results", [])

auth = Auth.Token(token)
gh = Github(auth=auth)
pr = gh.get_repo(repo_name).get_pull(int(pr_number))

if not issues:
    pr.create_issue_comment("✨ No issues found. Either you're a genius or you changed 0 lines.")
    exit(0)

body = [
    "## 🚨 Semgrep Automated Roast Review",
    "Scans code faster than PR reviewers run to coffee.\n"
]

def format_code(snippet):
    clean = snippet.strip()
    if clean.lower() == "requires login":
        return ""
    return f"```diff\n- {clean}\n```"

for i, issue in enumerate(issues, 1):
    raw_rule = issue.get("check_id", "unknown")
    rule = raw_rule.replace("semgrep-rules.", "")
    meta = SASSY_RULE_GUIDE.get(rule, {})

    file = issue["path"]
    start_line = issue["start"]["line"]
    msg = issue["extra"].get("message", "Fix required.")
    severity = issue["extra"].get("severity", "warning").upper()
    why_bad = meta.get("why", msg)
    fix = meta.get("fix", "Fix it properly.")
    roast = meta.get("roast", "Try harder.")
    snippet = format_code(issue["extra"].get("lines", ""))

    body.append("---")
    body.append(f"### 🔹 {i}. `{rule}` ({severity})")
    body.append(f"📍 Location: `{file}:{start_line}`")
    body.append(f"📌 **Why this is bad**: {why_bad}")
    body.append(f"**Semgrep said**: _{msg}_")

    if snippet:
        body.append(f"**Offending Code:**\n{snippet}")

    body.append(f"**How to fix:**\n```diff\n+ {fix}\n```")
    body.append(f"**Roast:** 🔥 {roast}\n")

comment = "\n".join(body)
pr.create_issue_comment(comment)

print("💬 Sassy PR comment posted successfully.")

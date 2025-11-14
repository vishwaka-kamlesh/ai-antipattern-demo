import os
import json
from github import Github, Auth

token = os.getenv("GITHUB_TOKEN")
repo_name = os.getenv("GITHUB_REPOSITORY")
pr_number = os.getenv("PR_NUMBER")

auth = Auth.Token(token)
gh = Github(auth=auth)
pr = gh.get_repo(repo_name).get_pull(int(pr_number))

issues = json.load(open("ai_output.json"))
issues = issues if isinstance(issues, list) else []

body = []
body.append("## 🤖 Automated Code Review – Judging You So You Get Better\n")

if not issues:
    body.append("✨ No detectable anti-patterns in this PR. Proud of you... this time.\n")
else:
    body.append("🚨 Code police caught something! \n\n")

for idx, it in enumerate(issues, 1):
    file = it.get("file", "?")
    line = it.get("line", "?")
    issue = it.get("issue", "Unknown")
    severity = it.get("severity", "Medium")
    explanation = it.get("explanation", "")
    fix = it.get("detailed_fix", "")
    patch = it.get("code_patch", "")
    risk = it.get("risk", "Unknown")

    emoji = {"Critical": "🛑", "High": "🚧", "Medium": "⚠️", "Low": "ℹ️"}.get(severity, "❓")

    body.append(f"---\n### {emoji} Issue {idx}: {issue}")
    body.append(f"📍 Location: `{file}` line {line}")
    body.append(f"🏷 Severity: **{severity}**")
    body.append(f"🧠 Why it matters:\n> {explanation}")
    body.append(f"🔧 Suggested Fix:\n> {fix}")

    if patch:
        body.append("\n```java")
        body.append(patch)
        body.append("```")

    body.append(f"☢ Risk if ignored: {risk}\n")

comment = "\n".join(body)

if len(comment) > 60000:
    comment = comment[:60000] + "\n\n...(trimmed due to size)"
    print("⚠️ Comment trimmed")

pr.create_issue_comment(comment)
print("💬 Comment posted successfully")

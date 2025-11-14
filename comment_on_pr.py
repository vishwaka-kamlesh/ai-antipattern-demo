import os, json, re
from github import Github, Auth

token = os.getenv("GITHUB_TOKEN")
repo_name = os.getenv("GITHUB_REPOSITORY")
pr_number = os.getenv("PR_NUMBER")

auth = Auth.Token(token)
gh = Github(auth=auth)
pr = gh.get_repo(repo_name).get_pull(int(pr_number))

print("🔗 Loaded PR context")

# Load processed AI JSON
data = json.load(open("ai_output.json"))
issues = data if isinstance(data, list) else []

body_lines = []
body_lines.append("## 🤖 AI Code Review – Automated but not Heartless\n")
body_lines.append("Thanks for the PR! Here's what I spotted:\n")

if not issues:
    body_lines.append("🎯 No anti-patterns detected! Clean code, clean conscience.\n")

for i, it in enumerate(issues, 1):
    file = it.get("file", "?")
    line = it.get("line", "?")
    issue = it.get("issue", "Issue detected")
    severity = it.get("severity", "Medium")
    explanation = it.get("explanation", "")
    fix = it.get("detailed_fix", "")
    patch = it.get("code_patch", "")
    risk = it.get("risk", "Unknown")

    emoji = {
        "Critical": "🛑",
        "High": "🚧",
        "Medium": "🟡",
        "Low": "🟢"
    }.get(severity, "⚪")

    body_lines.append(f"---\n### {emoji} {i}. {issue}")
    body_lines.append(f"**Location:** `{file}` line {line}")
    body_lines.append(f"**Severity:** **{severity}**\n")
    body_lines.append(f"**Why it matters:** {explanation}\n")
    body_lines.append(f"**Suggested Improvement:** {fix}\n")

    if patch:
        body_lines.append("```java")
        body_lines.append(patch)
        body_lines.append("```")

    body_lines.append(f"**Risk if ignored:** {risk}\n")

comment_body = "\n".join(body_lines)

# Trim if too long
if len(comment_body) > 60000:
    comment_body = comment_body[:60000] + "\n\n...(trimmed for readability)"
    print("⚠️ Comment trimmed")

pr.create_issue_comment(comment_body)
print("💬 Comment posted successfully")

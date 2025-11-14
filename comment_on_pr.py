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
body.append("## 🤖 AI Code Review – Automated but not Heartless")
body.append("Thanks for the PR! Here’s what I spotted:\n")

if not issues:
    body.append("🎉 No anti-patterns in this diff. Keep it clean 💪\n")

for idx, it in enumerate(issues, 1):
    file = it.get("file", "?")
    line = it.get("line", "?")
    issue = it.get("issue", "Issue detected")
    severity = it.get("severity", "Medium")
    explanation = it.get("explanation", "")
    fix = it.get("detailed_fix", "")
    patch = it.get("code_patch", "")
    risk = it.get("risk", "Unknown")

    emoji = {"Critical":"🛑","High":"🚧","Medium":"🟡","Low":"🟢"}.get(severity,"⚪")

    body.append(f"---\n### {emoji} {idx}. {issue}")
    body.append(f"**Location:** `{file}` line {line}")
    body.append(f"**Severity:** **{severity}**\n")
    body.append(f"**Why it matters:** {explanation}")
    body.append(f"**Suggested Fix:** {fix}")

    if patch:
        body.append("```java")
        body.append(patch)
        body.append("```")

    body.append(f"**Risk if ignored:** {risk}\n")

comment = "\n".join(body)

if len(comment) > 60000:
    comment = comment[:60000] + "\n\n...(trimmed for readability)"
    print("⚠️ Comment trimmed")

pr.create_issue_comment(comment)
print("💬 Comment posted successfully")

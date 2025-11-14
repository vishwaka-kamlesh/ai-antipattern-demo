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
body.append("## 🤖 Automated Code Review 😎🔥\n")

if not issues:
    body.append("✨ Surprisingly clean code. I'll allow it.\n")
else:
    body.append("🚨 Suspicious code detected, commence roasting 👇\n")

sev_map = {
    "Critical": "🛑 Critical",
    "High": "🚧 High",
    "Medium": "⚠️ Medium",
    "Low": "ℹ️ Low",
    "ERROR": "🚧 High"
}

for i, it in enumerate(issues, 1):
    body.append("---")

    body.append(f"### 🔥 Issue {i}: {it.get('issue','Unknown')}")
    body.append(f"📍 `{it.get('file','?')}` line {it.get('line','?')}")
    body.append(f"🏷 Severity: {sev_map.get(it.get('severity','Medium'),'⚠️')}")
    body.append(f"\n🧠 Why:\n{it.get('explanation','')}")
    body.append(f"\n🔧 Fix:\n{it.get('detailed_fix','')}")

    patch = it.get("code_patch","")
    if patch:
        body.append("```java")
        body.append(patch)
        body.append("```")

    body.append(f"☢ Risk:\n{it.get('risk','Unknown risk')}\n")

comment = "\n".join(body)

if len(comment) > 60000:
    comment = comment[:60000] + "\n\n...comment trimmed"
    print("⚠️ Comment too long, trimmed.")

pr.create_issue_comment(comment)
print("💬 Comment posted successfully 😌")

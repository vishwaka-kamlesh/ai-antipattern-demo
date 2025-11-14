import os
import json
from github import Github, Auth

token = os.getenv("GITHUB_TOKEN")
repo_name = os.getenv("GITHUB_REPOSITORY")
pr_number = os.getenv("PR_NUMBER")

if not token or not repo_name or not pr_number:
    print("❌ Missing required env vars for GitHub PR comment.")
    exit(1)

auth = Auth.Token(token)
gh = Github(auth=auth)
pr = gh.get_repo(repo_name).get_pull(int(pr_number))

# Load AI output
try:
    issues = json.load(open("ai_output.json", "r", encoding="utf-8"))
    if not isinstance(issues, list):
        issues = []
except:
    print("❌ Failed to load ai_output.json")
    issues = []

body = []
body.append("## 🤖 AI Code Review: Roasting With Love 💻🔥\n")

if not issues:
    body.append("✨ All clean here. For now... 😏\n")
else:
    body.append("🚨 Code police spotted some suspicious lines 👇\n")

severity_map = {
    "Critical": "🛑 Critical",
    "High": "🚧 High",
    "Medium": "⚠️ Medium",
    "Low": "ℹ️ Low",
    "ERROR": "🚧 High"
}

for idx, it in enumerate(issues, 1):
    file = it.get("file", "?")
    line = it.get("line", "?")
    issue = it.get("issue", "Unknown Issue")
    sev = it.get("severity", "Medium")
    severity = severity_map.get(sev, sev)
    explanation = it.get("explanation", "No explanation provided.")
    fix = it.get("detailed_fix", "Consider fixing this.")
    patch = it.get("code_patch", "")
    risk = it.get("risk", "Unknown risk if ignored.")

    body.append(f"""
---
### 🔥 Issue {idx}: {issue}

📍 **Where:** `{file}` line {line}  
🏷 **Severity:** {severity}  

🧠 **Why it matters**  
{explanation}

🔧 **How to fix it**  
{fix}
""")

    if patch:
        body.append("```java")
        body.append(patch)
        body.append("```")

    body.append("☢ **Risk if ignored**")
    body.append(risk)
    body.append("")

comment = "\n".join(body)

# Avoid GitHub API rejection on long messages
if len(comment) > 60000:
    comment = comment[:60000] + "\n\n... (trimmed, blame GitHub)"
    print("⚠️ Comment trimmed")

try:
    pr.create_issue_comment(comment)
    print("💬 Comment posted successfully")
except Exception as e:
    print(f"❌ Failed to post comment: {e}")
    raise

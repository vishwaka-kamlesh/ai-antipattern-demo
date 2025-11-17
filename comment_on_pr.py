import os
import json
from github import Github, Auth

token = os.getenv("GITHUB_TOKEN")
repo_name = os.getenv("GITHUB_REPOSITORY")
pr_number = os.getenv("PR_NUMBER")

if not token or not repo_name or not pr_number:
    print("❌ Missing required environment variables GITHUB_TOKEN / GITHUB_REPOSITORY / PR_NUMBER")
    exit(1)

print("📥 Loading Semgrep results...")
try:
    data = json.load(open("results.json"))
except:
    print("⚠️ No results.json found. Exiting.")
    exit(0)

issues = data.get("results", [])

auth = Auth.Token(token)
gh = Github(auth=auth)
pr = gh.get_repo(repo_name).get_pull(int(pr_number))

if not issues:
    msg = "✨ No anti-patterns detected. Clean code. Respect."
    pr.create_issue_comment(msg)
    print("💬 Comment posted: No issues.")
    exit(0)

body = []
body.append("## 🚨 Semgrep Code Quality Review\n")
body.append(f"Detected **{len(issues)}** issue(s) in your PR:\n")

for i, issue in enumerate(issues, 1):
    file = issue.get("path")
    line = issue.get("start", {}).get("line", "?")
    rule = issue.get("check_id", "unknown")
    msg = issue.get("extra", {}).get("message", "No message")

    body.append(f"---")
    body.append(f"### {i}. `{rule}`")
    body.append(f"📍 {file}:{line}")
    body.append(f"> {msg}\n")

comment = "\n".join(body)
pr.create_issue_comment(comment)

print("💬 Comment posted successfully")

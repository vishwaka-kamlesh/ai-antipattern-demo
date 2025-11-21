import os
import json
from github import Github, Auth

SASSY_RULE_GUIDE = {
    "empty-catch-block": {
        "fix": "Add logging or rethrow exception inside catch",
        "roast": "Hiding crimes doesn’t make them legal.",
        "why": "Unlogged exceptions make debugging impossible."
    },
    "no-print-stacktrace": {
        "fix": "logger.error(\"Unexpected error\", e)",
        "roast": "StackTrace in prod is like yelling passwords.",
        "why": "printStackTrace leaks internals and isn’t structured logging."
    },
    "no-system-out": {
        "fix": "logger.info(\"message\")",
        "roast": "System.out belongs in college labs.",
        "why": "Bypasses logging infra, gets lost in prod."
    },
    "logging-sensitive-data": {
        "fix": "mask/redact sensitive data",
        "roast": "Might as well CC the hackers.",
        "why": "Leaking personal data makes compliance cry."
    },
    "hardcoded-credentials": {
        "fix": "move secrets to env or vault",
        "roast": "Who needs privacy anyway?",
        "why": "Secrets in code leak through repos and logs."
    },
    "sql-injection-concat": {
        "fix": "use prepared statements",
        "roast": "Giving attackers direct DB access?",
        "why": "String concat allows malicious SQL execution."
    },
    "resource-leak": {
        "fix": "use try-with-resources",
        "roast": "Your app is dripping memory everywhere.",
        "why": "Leaked connections exhaust resource pools."
    },
    "magic-numbers": {
        "fix": "replace with named constant",
        "roast": "What is 223? Your IQ? Mine? Unknown.",
        "why": "Numbers without context kill readability."
    }
}

ROASTS = [
    "Readable code? Not your hobby clearly.",
    "Even ransomware has better structure.",
    "Future devs will write curses in the comments.",
    "Architecturally unstable like your sleep cycle.",
]

# Env vars
token = os.getenv("GITHUB_TOKEN")
repo_name = os.getenv("GITHUB_REPOSITORY")
pr_number = os.getenv("PR_NUMBER")

if not token or not repo_name or not pr_number:
    print("❌ Missing environment variables!")
    exit(1)

print("📥 Reading Semgrep results...")
data = json.load(open("results.json"))
issues = data.get("results", [])

auth = Auth.Token(token)
gh = Github(auth=auth)
pr = gh.get_repo(repo_name).get_pull(int(pr_number))

if not issues:
    pr.create_issue_comment("✨ So clean. I’m suspicious.")
    exit(0)

body = [
    "## 🚨 Semgrep Roast Review",
    "Quality checks powered by sarcasm.\n"
]

for i, issue in enumerate(issues, 1):
    raw_rule = issue.get("check_id", "unknown")
    rule = raw_rule.lower().replace("semgrep-rules.", "")
    file = issue.get("path")
    severity = issue.get("extra", {}).get("severity", "warning").upper()
    msg = issue.get("extra", {}).get("message", "Fix required.")
    line = issue.get("start", {}).get("line", "?")

    snippet = ""
    if file and isinstance(line, int):
        try:
            with open(file, "r", encoding="utf-8") as src:
                snippet = src.readlines()[line - 1].rstrip()
        except:
            snippet = "[Couldn't extract source line]"

    mapping = SASSY_RULE_GUIDE.get(rule, {})
    why = mapping.get("why", "This hurts maintainability and humans.")
    fix = mapping.get("fix", "Refactor responsibly.")
    roast = mapping.get("roast", ROASTS[i % len(ROASTS)])

    body.append("---")
    body.append(f"### 🔹 {i}. `{rule}` ({severity})")
    body.append(f"📍 `{file}:{line}`")
    body.append(f"📌 **Why**: {why}")
    body.append(f"📌 **Issue**: {msg}")

    body.append("\n```diff")
    body.append(f"- {snippet}")
    body.append(f"+ {fix}")
    body.append("```")

    body.append(f"🔥 **Roast**: {roast}\n")

pr.create_issue_comment("\n".join(body))
print("💬 Commented on PR successfully.")

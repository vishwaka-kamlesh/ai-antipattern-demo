import os
import json
from github import Github, Auth

# 🔥 Better rule mapping with WHY explanations
SASSY_RULE_GUIDE = {
    "empty-catch-block": {
        "fix": "log or rethrow the exception",
        "roast": "Ignoring errors doesn’t make them go away.",
        "why": "Swallowing exceptions hides failures and corrupts program flow."
    },
    "no-print-stacktrace": {
        "fix": "logger.error(\"Unexpected error\", e)",
        "roast": "Your console isn’t a bug tracker.",
        "why": "printStackTrace leaks details and bypasses structured logs."
    },
    "no-system-out": {
        "fix": "logger.info(\"message\")",
        "roast": "System.out is for college labs, not real apps.",
        "why": "System.out kills observability and log routing in production."
    },
    "logging-sensitive-data": {
        "fix": "mask or redact sensitive data",
        "roast": "Why not just email the data to attackers too?",
        "why": "Leaking credentials or PII into logs is a major security risk."
    },
    "hardcoded-credentials": {
        "fix": "move secrets into env vars or vault",
        "roast": "Hackers appreciate your generosity.",
        "why": "Credentials in code leak through repos, logs, builds and screenshots."
    },
    "sql-injection-concat": {
        "fix": "use prepared statements",
        "roast": "SQLi speedrun world record attempt?",
        "why": "String concatenation allows attackers to execute arbitrary queries."
    },
    "resource-leak": {
        "fix": "use try-with-resources",
        "roast": "Leakier than my old bike’s fuel tank.",
        "why": "Unreleased resources cause memory leaks and pool exhaustion."
    },
    "magic-numbers": {
        "fix": "use a named constant",
        "roast": "Numbers without meaning belong in horror films.",
        "why": "Magic numbers destroy maintainability and readability."
    },
    "no-thread-sleep": {
        "fix": "use async / scheduled execution",
        "roast": "Thread.sleep: because blocking is fun, right?",
        "why": "Thread.sleep blocks critical threads and hurts performance."
    },
    "string-equals-operator": {
        "fix": "use .equals() instead",
        "roast": "Java is not JavaScript. == won’t save you.",
        "why": "Using == compares references not values, causing logic failures."
    },
    "dto-public-fields": {
        "fix": "make fields private with accessors",
        "roast": "Encapsulation out here begging for respect.",
        "why": "Public fields expose state and break object integrity."
    },
    "nplus1-query-lazy-loading": {
        "fix": "use JOIN FETCH / @EntityGraph",
        "roast": "Your DB is screaming into the void.",
        "why": "Repeated DB queries inside loops kill performance."
    },
    "nplus1-query-repository": {
        "fix": "batch fetch or JOIN FETCH",
        "roast": "Database says: stop calling me every line.",
        "why": "Repository calls in loops turn into dozens of queries."
    },
    "double-checked-locking-no-volatile": {
        "fix": "use volatile keyword",
        "roast": "Thread safety isn’t optional.",
        "why": "Without volatile, double-checked locking still breaks."
    },
    "arrays-aslist-primitive": {
        "fix": "use IntStream/boxed conversion",
        "roast": "Primitive arrays don’t socialize like object arrays.",
        "why": "Arrays.asList(primitive[]) treats the array as a single element."
    },
    "null-check-after-dereference": {
        "fix": "check null before dereferencing",
        "roast": "NullPointerException speedrunner spotted.",
        "why": "Checking null after deref is useless. Boom → NPE."
    },
}

ROASTS = [
    "I’ve seen malware with better structure.",
    "Even AI wouldn’t debug this voluntarily.",
    "When tech debt becomes generational debt.",
    "Architecturally unstable like your sleep schedule.",
    "Congrats, you invented chaos-as-a-service.",
    "Future devs will curse your entire bloodline.",
    "Readable code? Not your thing, clearly.",
    "This line needs therapy.",
    "Garbage collector filing abuse complaints.",
    "At least you’re consistent… consistently bad."
]

# Read environment variables
token = os.getenv("GITHUB_TOKEN")
repo_name = os.getenv("GITHUB_REPOSITORY")
pr_number = os.getenv("PR_NUMBER")

if not token or not repo_name or not pr_number:
    print("❌ Missing required environment variables!")
    exit(1)

print("📥 Loading Semgrep results...")
data = json.load(open("results.json"))
issues = data.get("results", [])

auth = Auth.Token(token)
gh = Github(auth=auth)
pr = gh.get_repo(repo_name).get_pull(int(pr_number))

if not issues:
    pr.create_issue_comment("✨ Zero issues. Your code is cleaner than my existential crisis.")
    exit(0)

body = [
    "## 🚨 Semgrep Automated Roast Review",
    "Scans code faster than reviewers run to coffee.\n"
]

for i, issue in enumerate(issues, 1):
    raw_rule = issue.get("check_id", "unknown")
    rule = raw_rule.replace("semgrep-rules.", "").lower()

    meta = issue.get("extra", {})
    msg = meta.get("message", "Fix required.")
    file = issue.get("path")
    line = issue.get("start", {}).get("line", "?")
    severity = meta.get("severity", "warning").upper()
    
    snippet = ""

    # Preferred: Semgrep raw code snippet
    if "lines" in meta and meta["lines"]:
        snippet = meta["lines"].strip()

    # Fallback: metavars sometimes hold snippet fragments
    elif "metavars" in meta:
        for mv in meta["metavars"].values():
            if "abstract_content" in mv:
                snippet = mv["abstract_content"].strip()
            break

    # Ultra fallback: include the message if code snippet missing
    if not snippet:
        snippet = msg.replace("\n", " ").strip()

    mapping = SASSY_RULE_GUIDE.get(rule, {})

    why = (
        meta.get("metadata", {}).get("impact") or
        meta.get("metadata", {}).get("category") or
        mapping.get("why") or
        "This practice can cause maintainability or security issues."
    )

    fix = mapping.get("fix", "Apply a suitable fix for this issue.")
    roast = mapping.get("roast") or ROASTS[i % len(ROASTS)]

    if snippet.lower() == "requires login":
        snippet = ""

    body.append("---")
    body.append(f"### 🔹 {i}. `{rule}` ({severity})")
    body.append(f"📍 Location: `{file}:{line}`")
    body.append(f"📌 Why this is bad: {why}")
    body.append(f"**Semgrep said:** {msg}")

    if snippet:
        body.append(f"\n```diff\n- {snippet}\n```\n")

    body.append(f"**How to fix:**\n```diff\n+ {fix}\n```")
    body.append(f"**Roast:** 🔥 {roast}\n")

pr.create_issue_comment("\n".join(body))
print("💬 Posted stylish review to PR like a legend.")

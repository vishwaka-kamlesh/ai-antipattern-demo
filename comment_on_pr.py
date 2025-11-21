import os
import json
from github import Github, Auth

# Rule-specific fixes & roasts (triple-quoted to avoid quote issues)
SASSY_RULE_GUIDE = {
    "empty-catch-block": {
        "fix": """log or rethrow the exception.""",
        "roast": """Ignoring errors doesn't make them go away."""
    },
    "no-print-stacktrace": {
        "fix": """logger.error("Unexpected error", e)""",
        "roast": """Your console isn’t a bug tracker bro."""
    },
    "no-system-out": {
        "fix": """logger.info("message")""",
        "roast": """System.out is only okay in first semester Java."""
    },
    "logging-sensitive-data": {
        "fix": """mask or redact sensitive data before logging.""",
        "roast": """That's one way to leak secrets into logs."""
    },
    "hardcoded-credentials": {
        "fix": """move secrets into environment or vault.""",
        "roast": """Hardcoding secrets is hacker fan service."""
    },
    "hardcoded-url": {
        "fix": """inject URLs via configuration.""",
        "roast": """DevOps will cry every deployment."""
    },
    "sql-injection-concat": {
        "fix": """use prepared statements.""",
        "roast": """SQL injection speedrun unlocked."""
    },
    "no-thread-sleep": {
        "fix": """use async or scheduled execution.""",
        "roast": """Thread.sleep() blocks threads like traffic jams."""
    },
    "string-concat-in-loop": {
        "fix": """use StringBuilder or joining().""",
        "roast": """GC pressure intensifies."""
    },
    "expensive-object-in-loop": {
        "fix": """reuse object outside loop.""",
        "roast": """New objects every iteration? Living rich."""
    },
    "nplus1-query-repository": {
        "fix": """use JOIN FETCH or batch fetching.""",
        "roast": """Your DB is not a personal diary."""
    },
    "nplus1-query-lazy-loading": {
        "fix": """prefetch using @EntityGraph or JOIN FETCH.""",
        "roast": """Lazy loading, lazy performance."""
    },
    "string-equals-operator": {
        "fix": """use .equals() instead.""",
        "roast": """This isn’t JavaScript — == won’t rescue you."""
    },
    "dto-public-fields": {
        "fix": """use private fields with accessors.""",
        "roast": """Encapsulation left the chat."""
    },
    "magic-numbers": {
        "fix": """use a named constant.""",
        "roast": """Random numbers aren’t documentation."""
    },
    "no-field-injection": {
        "fix": """use constructor injection.""",
        "roast": """Testing shouldn't feel like black magic."""
    },
    "catch-generic-exception": {
        "fix": """catch scoped exceptions instead.""",
        "roast": """Catching everything means fixing nothing."""
    },
    "resource-leak": {
        "fix": """use try-with-resources.""",
        "roast": """Leaks like a toddler with juice."""
    },
    "null-check-after-dereference": {
        "fix": """check for null first.""",
        "roast": """NPE speedrun any% PB attempt."""
    },
    "inefficient-empty-check": {
        "fix": """use .isEmpty().""",
        "roast": """Readability suffers in silence."""
    },
    "double-checked-locking-no-volatile": {
        "fix": """mark instance volatile.""",
        "roast": """Thread safety shouldn’t be optional."""
    },
    "boolean-comparison-with-equals": {
        "fix": """use .equals(Boolean.TRUE/FALSE).""",
        "roast": """Comparing booleans like comparing apples and chairs."""
    },
    "arrays-aslist-primitive": {
        "fix": """use IntStream/boxed conversion.""",
        "roast": """Primitive arrays refuse to socialize."""
    },
    "modify-collection-while-iterating-remove": {
        "fix": """use Iterator.remove().""",
        "roast": """ℹ️ ConcurrentModificationException entered the chat."""
    },
    "modify-collection-while-iterating-add": {
        "fix": """collect outside then modify.""",
        "roast": """Adding chaos one loop at a time."""
    },
    "bigdecimal-from-double": {
        "fix": """use BigDecimal.valueOf().""",
        "roast": """Precision is not optional in finance."""
    }
}

# Environment variables
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
    pr.create_issue_comment("✨ No issues found. Code is smelling like fresh refactor!")
    exit(0)

body = [
    "## 🚨 Semgrep Review with Style",
    "Automated code review with actionable suggestions and minimal tears.\n"
]

for i, issue in enumerate(issues, 1):
    rule = issue.get("check_id", "unknown")
    meta = SASSY_RULE_GUIDE.get(rule, {})

    file = issue.get("path")
    line = issue.get("start", {}).get("line", "?")
    msg = issue.get("extra", {}).get("message", "Fix required.")
    severity = issue.get("extra", {}).get("severity", "warning").upper()

    snippet = issue.get("extra", {}).get("lines", "").strip()
    fix_snippet = meta.get("fix", "Please apply proper fix here.")
    roast_text = meta.get("roast", "You can improve this part.")

    body.append("---")
    body.append(f"### 🔹 {i}. `{rule}` ({severity})")
    body.append(f"📍 **`{file}:{line}`**")
    body.append(f"**Issue:** {msg}\n")

    if snippet:
        body.append(f"```diff\n- {snippet}\n```")

    body.append(f"**Recommended Fix:**\n```diff\n+ {fix_snippet}\n```")
    body.append(f"**Roast:** 🥲 {roast_text}\n")

comment = "\n".join(body)
pr.create_issue_comment(comment)

print("💬 Stylish PR comment posted successfully.")

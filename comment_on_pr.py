import os
import json
from github import Github, Auth

SASSY_RULE_GUIDE = {
    "empty-catch-block": {
        "fix": "Log the exception or rethrow it",
        "roast": "Just pretending nothing happened? Cute.",
        "why": "Swallowed exceptions hide real failures and break debugging."
    },
    "no-print-stacktrace": {
        "fix": "Use logger.error(\"Unexpected error\", e)",
        "roast": "printStackTrace is the caveman’s debugger.",
        "why": "Leaks stack traces and ignores logging standards."
    },
    "no-system-out": {
        "fix": "Use SLF4J logger",
        "roast": "System.out belongs in hostel lab practicals.",
        "why": "Bypasses logging pipelines and breaks production observability."
    },
    "logging-sensitive-data": {
        "fix": "Mask or redact secrets before logging",
        "roast": "Why not send your passwords to public Slack too?",
        "why": "PII exposure violates security and compliance."
    },
    "hardcoded-credentials": {
        "fix": "Move secrets to environment/secret manager",
        "roast": "Hackers be like: appreciate you bro.",
        "why": "Credentials in code spread through repos and logs forever."
    },
    "hardcoded-url": {
        "fix": "Use @Value or config properties for URLs",
        "roast": "Hardcoding endpoints? Vendor lock-in speedrun.",
        "why": "Changing environments breaks if URLs stay embedded in code."
    },
    "sql-injection-concat": {
        "fix": "Use prepared statements",
        "roast": "One input field away from fame in a CVE database.",
        "why": "Attackers can inject malicious SQL into concatenated queries."
    },
    "no-thread-sleep": {
        "fix": "Use async scheduler or executor",
        "roast": "Freezing threads like you freeze in stand-ups.",
        "why": "Blocks thread pools and wrecks latency under load."
    },
    "string-concat-in-loop": {
        "fix": "Use StringBuilder or Stream.joining",
        "roast": "Temporary string objects filing harassment complaints.",
        "why": "Creates tons of temporary objects, hurting performance."
    },
    "expensive-object-in-loop": {
        "fix": "Move heavyweight object creation outside the loop",
        "roast": "CPU fan sounds like a rocket launch now.",
        "why": "Repeated expensive initialization wastes CPU and memory."
    },
    "nplus1-query-repository": {
        "fix": "Use JOIN FETCH, EntityGraph or batch fetching",
        "roast": "Database screaming: ‘Why call me 90 times for a list?’",
        "why": "Dozens of extra DB round trips destroy query performance."
    },
    "nplus1-query-lazy-loading": {
        "fix": "Use eager fetching strategies",
        "roast": "Lazy loading so lazy it overworks the DB.",
        "why": "Each loop iteration triggers additional queries."
    },
    "string-equals-operator": {
        "fix": "Use .equals() for string value comparison",
        "roast": "Java isn’t JavaScript and == isn’t your friend.",
        "why": "== compares references, causing hidden logic bugs."
    },
    "dto-public-fields": {
        "fix": "Make fields private with getters/setters",
        "roast": "Public fields? Your encapsulation got robbed.",
        "why": "Leaks internal state and breaks class invariants."
    },
    "magic-numbers": {
        "fix": "Replace literal with a named constant",
        "roast": "Is 397 your lucky number or a cry for help?",
        "why": "Unexplained constants weaken readability and maintainability."
    },
    "no-field-injection": {
        "fix": "Use constructor injection",
        "roast": "@Autowired fields ruin testability like an ex ruins peace.",
        "why": "Constructor injection enforces immutability and clear deps."
    },
    "catch-generic-exception": {
        "fix": "Catch specific exception types",
        "roast": "Catching Exception is like catching Covid with a paper mask.",
        "why": "Masks real errors and prevents meaningful handling."
    },
    "resource-leak": {
        "fix": "Use try-with-resources properly",
        "roast": "Connections leaking faster than your weekend plans.",
        "why": "Unclosed streams and DB handles exhaust memory/thread pools."
    },
    "null-check-after-dereference": {
        "fix": "Check for null *before* calling methods",
        "roast": "NPE speedrun world record attempt?",
        "why": "The null check is useless after dereferencing the variable."
    },
    "inefficient-empty-check": {
        "fix": "Use .isEmpty() instead",
        "roast": "This condition is more bloated than your backlog.",
        "why": "Simplifies checks and avoids extra operations."
    },
    "double-checked-locking-no-volatile": {
        "fix": "Add volatile keyword to instance field",
        "roast": "Multi-threading without volatile… daring.",
        "why": "Without volatile, state may never become visible to threads."
    },
    "boolean-comparison-with-equals": {
        "fix": "Use Boolean.TRUE.equals(var)",
        "roast": "== for Boolean? QA thanks you for the extra work.",
        "why": "Avoids reference comparison and inconsistent truth tests."
    },
    "arrays-aslist-primitive": {
        "fix": "Use IntStream/boxed or manual conversion",
        "roast": "Primitive arrays didn’t ask to be treated as objects.",
        "why": "Arrays.asList(primitive[]) treats whole array as one element."
    },
    "modify-collection-while-iterating-remove": {
        "fix": "Use Iterator.remove()",
        "roast": "ConcurrentModificationException just waiting to erupt.",
        "why": "Removing during iteration corrupts collection state."
    },
    "modify-collection-while-iterating-add": {
        "fix": "Collect separately or use iterator",
        "roast": "Chaos-engineering by accident.",
        "why": "Adding during iteration triggers concurrency faults."
    },
    "bigdecimal-from-double": {
        "fix": "Use BigDecimal.valueOf(double)",
        "roast": "Loss of precision like losing socks in laundry.",
        "why": "double → BigDecimal introduces rounding errors."
    },
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
    "## 🚨Code Police",
    "We catch the bugs you create, so you don't have to wake at 2 am debugging the production.\n"
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

    body.append(f"📌 **Line causing issue**")
    body.append("\n```diff")
    body.append(f"- {snippet}")
    body.append("```")
    
    body.append(f"📌 **How to fix**")
    body.append("\n```diff")
    body.append(f"+ {fix}")
    body.append("```")

    body.append(f"{roast}\n")

pr.create_issue_comment("\n".join(body))
print("💬 Commented on PR successfully.")

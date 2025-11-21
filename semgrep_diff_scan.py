import os
import json
import subprocess
import sys
import re

print("🔍 Running Diff-Optimized Semgrep Scanner...")

# Base commit against main
BASE_SHA = subprocess.getoutput("git merge-base HEAD origin/main").strip()
print(f"📌 Base commit: {BASE_SHA}")

# Files changed in this PR
changed_files = subprocess.getoutput(
    f"git diff --name-only {BASE_SHA}"
).splitlines()
print(f"📄 Changed files detected: {changed_files}")

if not changed_files:
    print("✨ No changed files found!")
    json.dump({"results": []}, open("results.json", "w"))
    sys.exit(0)

results = []

for file_path in changed_files:
    # Only care about Java files
    if not file_path.endswith(".java"):
        continue

    if not os.path.exists(file_path):
        continue

    # Get diff hunks for this file
    diff_output = subprocess.getoutput(
        f"git diff -U0 {BASE_SHA} -- {file_path}"
    )

    hunks = re.findall(r"@@ \-(\d+),?\d* \+(\d+),?(\d*) @@", diff_output)

    if not hunks:
        continue

    # Collect all changed line numbers for this file
    changed_lines = set()
    for _, new_start, length in hunks:
        new_start = int(new_start)
        length = int(length) if length else 1
        for line_no in range(new_start, new_start + length):
            changed_lines.add(line_no)

    if not changed_lines:
        continue

    print(f"▶ Scanning {file_path} (lines changed: {sorted(changed_lines)[:10]}...)")

    # Run Semgrep ONCE per file
    cmd = [
        "semgrep",
        "scan",
        "--config", "semgrep-rules",
        "--json",
        "--disable-version-check",
        "--quiet",
        file_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stderr:
        # Just log; Semgrep likes to talk a lot
        print("⚠️ Semgrep stderr:\n", result.stderr)

    sg_output = result.stdout
    json_start = sg_output.find("{")
    if json_start == -1:
        continue

    parsed = json.loads(sg_output[json_start:])

    # Keep only findings whose start.line is in the diff
    for issue in parsed.get("results", []):
        start_line = issue.get("start", {}).get("line")
        if isinstance(start_line, int) and start_line in changed_lines:
            issue["path"] = file_path
            results.append(issue)

print(f"✨ Completed. Total issues detected in diff: {len(results)}")
json.dump({"results": results}, open("results.json", "w"), indent=2)

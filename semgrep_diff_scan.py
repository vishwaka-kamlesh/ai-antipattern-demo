import os
import json
import subprocess
import tempfile
import sys
import re

print("🔍 Extracting changed code for Semgrep scanning...")

# Determine base commit for diff
BASE_SHA = subprocess.getoutput("git merge-base HEAD origin/main").strip()
print(f"📌 Using base commit: {BASE_SHA}")

# Files changed in this PR
changed_files = subprocess.getoutput(f"git diff --name-only {BASE_SHA}").splitlines()

if not changed_files:
    print("✨ No changed files. Writing empty results.")
    with open("results.json", "w") as f:
        json.dump({"results": []}, f)
    sys.exit(0)

results = []

for file_path in changed_files:
    if not os.path.exists(file_path):
        continue

    diff_output = subprocess.getoutput(f"git diff -U0 {BASE_SHA} -- {file_path}")
    hunks = re.findall(r"@@ \-(\\d+),?\\d* \\+(\\d+),?(\\d*) @@", diff_output)

    if not hunks:
        continue

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for _, new_start, length in hunks:
        new_start = int(new_start)
        length = int(length) if length else 1

        # Extract only changed block
        chunk = "".join(lines[new_start - 1:new_start - 1 + length])

        # Preserve correct file extension for Semgrep language detection
        file_ext = os.path.splitext(file_path)[1] or ".txt"

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            tmp.write(chunk.encode("utf-8"))
            tmp_path = tmp.name

        # Run Semgrep only on extracted hunk
        sg_output = subprocess.getoutput(f"semgrep --config semgrep-rules --json {tmp_path}")

        try:
            parsed = json.loads(sg_output)
        except Exception:
            continue

        for issue in parsed.get("results", []):
            issue["path"] = file_path

            # Adjust back to original file line numbers
            if "start" in issue:
                issue["start"]["line"] += new_start - 1
            if "end" in issue:
                issue["end"]["line"] += new_start - 1

            results.append(issue)

# Save merged results
with open("results.json", "w", encoding="utf-8") as f:
    json.dump({"results": results}, f, indent=2)

print(f"✨ Diff scan completed. Found {len(results)} relevant issues.")

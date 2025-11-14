import os
import json
import subprocess
import tempfile
import sys
import re

print("🔍 Running Diff-Optimized Semgrep Scanner...")

# Ensure we have the base commit
subprocess.run(["git", "fetch", "origin", "main"], check=False)
BASE_SHA = subprocess.getoutput("git merge-base HEAD origin/main").strip()

print(f"📌 Base commit: {BASE_SHA}")

changed_files = subprocess.getoutput(f"git diff --name-only {BASE_SHA}").splitlines()
results = []

if not changed_files:
    print("✨ No changed files. Writing empty results.")
    json.dump({"results": []}, open("results.json", "w"), indent=2)
    sys.exit(0)

for file_path in changed_files:
    if not os.path.exists(file_path):
        continue

    diff_output = subprocess.getoutput(f"git diff -U0 {BASE_SHA} -- {file_path}")
    hunks = re.findall(r"@@ \-(\d+),?\d* \+(\d+),?(\d*) @@", diff_output)

    if not hunks:
        continue

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for _, new_start, length in hunks:
        new_start = int(new_start)
        length = int(length) if length else 1
        chunk = "".join(lines[new_start - 1:new_start - 1 + length]).strip()

        # Skip empty
        if not chunk.strip():
            continue

        file_ext = os.path.splitext(file_path)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            tmp.write(chunk.encode("utf-8"))
            tmp_path = tmp.name

        sg_output = subprocess.getoutput(f"semgrep --config semgrep-rules --json {tmp_path}")

        try:
            parsed = json.loads(sg_output)
        except:
            continue

        for issue in parsed.get("results", []):
            issue["path"] = file_path

            # Normalize correct file line
            if "start" in issue:
                issue["start"]["line"] += new_start - 1
            if "end" in issue:
                issue["end"]["line"] += new_start - 1

            # ✔ Add actual broken code snippet
            issue["code"] = chunk

            results.append(issue)

json.dump({"results": results}, open("results.json", "w"), indent=2)
print(f"✨ Completed. Total issues detected: {len(results)}")

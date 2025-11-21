import os
import json
import subprocess
import tempfile
import sys
import re

print("🔍 Running Diff-Optimized Semgrep Scanner...")

BASE_SHA = subprocess.getoutput("git merge-base HEAD origin/main").strip()
print(f"📌 Base commit: {BASE_SHA}")

changed_files = subprocess.getoutput(f"git diff --name-only {BASE_SHA}").splitlines()
print(f"📄 Changed files detected: {changed_files}")

if not changed_files:
    print("✨ No changed files found!")
    json.dump({"results": []}, open("results.json", "w"))
    sys.exit(0)

results = []

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

        chunk = "".join(lines[new_start - 1:new_start - 1 + length])
        file_ext = os.path.splitext(file_path)[1] or ".txt"

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext, mode='w', encoding='utf-8') as tmp:
            tmp.write(chunk)
            tmp_path = tmp.name

        # Working Semgrep configuration directory
        cmd = [
            "semgrep",
            "scan",
            "--config", "semgrep-rules",
            "--json",
            "--max-chars-per-line", "200",
            "--max-lines-per-finding", "5",
            tmp_path
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            # Log stderr if rules misconfigured
            if result.stderr:
                print("⚠️ Semgrep stderr:\n", result.stderr)

            sg_output = result.stdout
            json_start = sg_output.find('{')
            if json_start == -1:
                continue

            parsed = json.loads(sg_output[json_start:])

            for issue in parsed.get("results", []):
                issue["path"] = file_path
                issue["start"]["line"] += new_start - 1
                issue["end"]["line"] += new_start - 1
                results.append(issue)

        finally:
            try:
                os.unlink(tmp_path)
            except:
                pass

print(f"✨ Completed. Total issues detected: {len(results)}")
json.dump({"results": results}, open("results.json", "w"), indent=2)

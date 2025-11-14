import os
import json
import subprocess
import sys
import re

print("🔍 Running Diff-Optimized Semgrep Scanner...")

# Determine base commit for diff detection
BASE_SHA = subprocess.getoutput("git merge-base HEAD origin/main").strip()
print(f"📌 Base commit: {BASE_SHA}")

# Get changed files
changed_files = subprocess.getoutput(f"git diff --name-only {BASE_SHA}").splitlines()
print(f"📄 Changed files detected: {changed_files}")

if not changed_files:
    print("✨ No changed files found!")
    json.dump({"results": []}, open("results.json", "w"))
    sys.exit(0)

results = []

for file_path in changed_files:
    if not os.path.exists(file_path):
        print(f"⚠️ Skipping missing file: {file_path}")
        continue

    print(f"\n📁 Checking file: {file_path}")

    diff_output = subprocess.getoutput(f"git diff -U0 {BASE_SHA} -- {file_path}")
    print(f"🔍 Raw diff:\n{diff_output}")

    hunks = re.findall(r"@@ \-(\d+),?\d* \+(\d+),?(\d*) @@", diff_output)
    print(f"📌 Hunks found: {hunks}")

    if not hunks:
        print("⚠️ No hunks found in this file, skipping")
        continue

    for _, new_start, length in hunks:
        new_start = int(new_start)
        length = int(length) if length else 1
        print(f"➡️ Adding changed region: file={file_path} start={new_start} length={length}")

        results.append({
            "path": file_path,
            "start": {"line": new_start},
            "end": {"line": new_start + length - 1}
        })

print("\n====== FINAL RESULTS ======")
print(results)

json.dump({"results": results}, open("results.json", "w"), indent=2)
print(f"✨ Completed. Total issues detected: {len(results)}")

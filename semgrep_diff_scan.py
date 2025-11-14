import os
import json
import subprocess
import tempfile
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

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for _, new_start, length in hunks:
        new_start = int(new_start)
        length = int(length) if length else 1
        print(f"➡️ Extracting chunk: start={new_start} length={length}")

        chunk = "".join(lines[new_start - 1:new_start - 1 + length])
        print(f"🧩 Code chunk:\n{chunk}")

        file_ext = os.path.splitext(file_path)[1] or ".txt"
        print(f"📌 File extension for chunk: {file_ext}")

        # Write chunk to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext, mode='w', encoding='utf-8') as tmp:
            tmp.write(chunk)
            tmp_path = tmp.name

        print(f"📍 Temp chunk file created: {tmp_path}")

        # Run Semgrep on chunk
        cmd = ["semgrep", "--config", "semgrep-rules", "--json", tmp_path]
        print(f"⚙️ Running Semgrep: {' '.join(cmd)}")

        try:
            # Use subprocess.run to properly capture output
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            sg_output = result.stdout
            print(f"📊 Semgrep result raw:\n{sg_output}")
            
            # Extract JSON from output (handle warnings/text before JSON)
            json_start = sg_output.find('{')
            if json_start > 0:
                print(f"⚠️ Stripping non-JSON prefix ({json_start} chars)")
                sg_output = sg_output[json_start:]
            elif json_start == -1:
                print(f"❌ No JSON found in output")
                continue

            parsed = json.loads(sg_output)
            print(f"📌 Parsed issues: {parsed.get('results', [])}")
            
            for issue in parsed.get("results", []):
                issue["path"] = file_path
                issue["start"]["line"] += new_start - 1
                issue["end"]["line"] += new_start - 1
                results.append(issue)
                
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse Semgrep JSON: {e}")
            print(f"📄 First 200 chars: {sg_output[:200]}")
        except subprocess.TimeoutExpired:
            print(f"❌ Semgrep timed out on {tmp_path}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except:
                pass

print("\n====== FINAL RESULTS ======")
print(results)

json.dump({"results": results}, open("results.json", "w"), indent=2)
print(f"✨ Completed. Total issues detected: {len(results)}")
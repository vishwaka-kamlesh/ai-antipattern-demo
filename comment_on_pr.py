import os
import json
import re
from github import Github, Auth

# --------------------------------------------------------------------
#  DETECT PR CONTEXT
# --------------------------------------------------------------------
repo_name = os.getenv("GITHUB_REPOSITORY")
ref = os.getenv("GITHUB_REF", "")
pr_number = os.getenv("PR_NUMBER")

if not pr_number:
    if "refs/pull/" in ref:
        try:
            pr_number = ref.split("/")[2]
        except IndexError:
            pr_number = None

if not pr_number:
    raise ValueError("❌ Unable to determine pull request number from environment variables.")

pr_number = int(pr_number)
print(f"📋 Working with PR #{pr_number}")

# --------------------------------------------------------------------
#  CONNECT TO GITHUB
# --------------------------------------------------------------------
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise ValueError("❌ Missing GITHUB_TOKEN environment variable.")

# Use new authentication method
auth = Auth.Token(token)
gh = Github(auth=auth)
repo = gh.get_repo(repo_name)
pr = repo.get_pull(pr_number)

print(f"✅ Connected to repository: {repo_name}")

# --------------------------------------------------------------------
#  LOAD AI OUTPUT
# --------------------------------------------------------------------
if not os.path.exists("ai_output.json"):
    raise FileNotFoundError("❌ ai_output.json not found — ensure post_to_hf.py ran successfully.")

with open("ai_output.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

print(f"📦 Loaded ai_output.json, type: {type(raw)}")

# --------------------------------------------------------------------
#  PARSE AI OUTPUT ROBUSTLY
# --------------------------------------------------------------------
issues = []

if isinstance(raw, list):
    # Already a list of issues
    issues = raw
    print(f"✅ Direct list format: {len(issues)} issues")
    
elif isinstance(raw, dict):
    # Check if it's API response format
    if "choices" in raw:
        content = raw["choices"][0]["message"]["content"]
        print(f"📝 Extracted content from API response format")
    else:
        # Might be a single issue wrapped in dict
        issues = [raw]
        print(f"✅ Single issue dict format")
        content = None
    
    # Try to parse the content if we extracted it
    if content:
        # Remove markdown code blocks
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        content = content.strip()
        
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list):
                issues = parsed
                print(f"✅ Parsed JSON array: {len(issues)} issues")
            elif isinstance(parsed, dict):
                issues = [parsed]
                print(f"✅ Parsed single JSON object")
        except json.JSONDecodeError as e:
            print(f"⚠️  Could not parse content as JSON: {e}")
            print(f"Content preview: {content[:200]}")
            issues = [{
                "file": "N/A",
                "line": "?",
                "issue": "AI Analysis Available",
                "explanation": content[:500] + "..." if len(content) > 500 else content
            }]
            
elif isinstance(raw, str):
    # Raw string output
    print(f"📝 String format detected")
    
    # Remove markdown code blocks
    clean = re.sub(r'```json\s*', '', raw)
    clean = re.sub(r'```\s*', '', clean)
    clean = clean.strip()
    
    try:
        parsed = json.loads(clean)
        if isinstance(parsed, list):
            issues = parsed
            print(f"✅ Parsed string to JSON array: {len(issues)} issues")
        elif isinstance(parsed, dict):
            issues = [parsed]
            print(f"✅ Parsed string to single JSON object")
    except json.JSONDecodeError:
        print(f"⚠️  String is not valid JSON, using as-is")
        issues = [{
            "file": "N/A",
            "line": "?",
            "issue": "AI Analysis",
            "explanation": clean[:500] + "..." if len(clean) > 500 else clean
        }]

if not issues:
    print("⚠️  No issues to post")
    exit(0)

print(f"📊 Processing {len(issues)} issues for PR comment")

# --------------------------------------------------------------------
#  BUILD MARKDOWN COMMENT
# --------------------------------------------------------------------
body_lines = ["### 🤖 AI Detailed Anti-Pattern Review\n"]

for idx, it in enumerate(issues, 1):
    if not isinstance(it, dict):
        print(f"⚠️  Issue {idx} is not a dict, skipping: {type(it)}")
        continue
    
    file = it.get("file", "?")
    line = it.get("line", "?")
    issue = it.get("issue", "")
    severity = it.get("severity", "")
    explanation = it.get("explanation", "")
    detailed_fix = it.get("detailed_fix", "")
    code_patch = it.get("code_patch", "")
    tests = it.get("tests", "")
    risk = it.get("risk", "")
    refs = it.get("references", [])

    body_lines.append(f"#### Issue #{idx}")
    body_lines.append(f"**File:** `{file}` (line {line})")
    
    if severity:
        emoji = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(severity, "⚪")
        body_lines.append(f"**Severity:** {emoji} {severity}")
    
    if issue:
        body_lines.append(f"**Issue:** {issue}")
    
    if explanation:
        body_lines.append(f"\n**Explanation:**\n{explanation}")
    
    if detailed_fix:
        body_lines.append(f"\n**Detailed Fix:**\n{detailed_fix}")
    
    if code_patch:
        body_lines.append("\n**Suggested Code Patch:**")
        body_lines.append("```java")  # Or detect language
        body_lines.append(code_patch)
        body_lines.append("```")
    
    if tests:
        body_lines.append(f"\n**Suggested Tests:**\n{tests}")
    
    if risk:
        body_lines.append(f"\n**Risk:**\n{risk}")
    
    if refs and isinstance(refs, list):
        body_lines.append("\n**References:**")
        for r in refs:
            body_lines.append(f"- {r}")
    
    body_lines.append("\n---\n")

comment_body = "\n".join(body_lines)

# Limit comment size (GitHub has limits)
if len(comment_body) > 65000:
    comment_body = comment_body[:65000] + "\n\n... (truncated due to length)"
    print("⚠️  Comment truncated to fit GitHub limits")

# --------------------------------------------------------------------
#  POST COMMENT TO PR
# --------------------------------------------------------------------
try:
    pr.create_issue_comment(comment_body)
    print(f"✅ Posted AI detailed anti-pattern report to PR #{pr_number}")
except Exception as e:
    print(f"❌ Failed to post comment: {e}")
    raise
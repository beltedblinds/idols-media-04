#!/usr/bin/env python3
import os
import subprocess
from urllib.parse import urlparse, unquote

LINKS_FILE = "idol_gallery_links_04.txt"
DATES_FILE = "idol_gallery_dates_04.txt"

def raw_url_to_relpath(raw_url):
    parsed = urlparse(raw_url)
    path = unquote(parsed.path)
    # strip /user/repo/branch/
    return "/".join(path.split("/")[4:])

# -----------------------------
# Build first-commit map (ONE Git call)
# -----------------------------
print("⏳ Building first-commit map…")
commit_map = {}
current_date = None

# suppress stderr to avoid red lines
log_output = subprocess.check_output(
    ["git", "log", "--diff-filter=A", "--name-only", "--format=%cI"],
    text=True,
    stderr=subprocess.DEVNULL
)

for line in log_output.splitlines():
    line = line.strip()
    if not line:
        continue
    if line[0].isdigit():
        current_date = line
        continue
    if current_date and line not in commit_map:
        commit_map[line] = current_date

print(f"✅ Indexed {len(commit_map)} commit dates")

# -----------------------------
# Process links in order
# -----------------------------
output_lines = []

if not os.path.exists(LINKS_FILE):
    raise SystemExit(f"{LINKS_FILE} not found")

with open(LINKS_FILE, "r", encoding="utf-8") as f:
    for line in f:
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 2:
            continue
        raw_url = parts[1]
        rel_path = raw_url_to_relpath(raw_url)
        commit_date = commit_map.get(rel_path, "")
        output_lines.append(f"{rel_path}, {commit_date}")

# -----------------------------
# Write output
# -----------------------------
with open(DATES_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print(f"📄 Generated {DATES_FILE} (Fast Pass)")

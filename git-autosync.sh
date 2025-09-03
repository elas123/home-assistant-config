#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/Users/frank/home-assistant-project"
MSG_PREFIX="autosync"
MAX_SIZE=$((25*1024*1024)) # 25MB

cd "$REPO_DIR"

# Skip if a rebase/merge is in progress
if [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ] || [ -f .git/MERGE_HEAD ]; then
  exit 0
fi

# 0) Clean all ignored junk from working tree (matches .gitignore & global ignores)
git clean -fdX >/dev/null 2>&1 || true

# 1) Stage everything that isn't ignored
git add -A

# 2) Safety: don't commit secrets
if git diff --cached --name-only | grep -E '^secrets\.yaml$|\.yaml\.secret$' >/dev/null 2>&1; then
  echo "❌ autosync blocked: secrets present (secrets.yaml / *.yaml.secret)."
  exit 1
fi

# 3) Safety: block very large files
while IFS= read -r f; do
  [ -f "$f" ] || continue
  sz=$(wc -c < "$f" 2>/dev/null || echo 0)
  if [ "$sz" -gt "$MAX_SIZE" ]; then
    echo "❌ autosync blocked: '$f' is >25MB ($sz bytes)."
    exit 1
  fi
done < <(git diff --cached --name-only)

# 4) If no staged changes, do nothing
if git diff --cached --quiet --ignore-submodules --; then
  exit 0
fi

# 5) Commit with timestamp and push
ts=$(date +"%Y-%m-%d %H:%M:%S")
git commit -m "$MSG_PREFIX: $ts" >/dev/null 2>&1 || exit 0
branch=$(git rev-parse --abbrev-ref HEAD)
git push -u origin "$branch" >/dev/null 2>&1 || git push -u origin "$branch"
echo "✅ autosync: committed & pushed on $branch at $ts"

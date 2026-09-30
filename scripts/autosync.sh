#!/bin/sh
# End-of-turn auto-sync. Commits and pushes any uncommitted change in the repos below, so an edit
# made by Claude (or by you) is backed up and reaches every surface without a manual commit.
#
# Install as a Claude Code Stop hook in ~/.claude/settings.json:
#   "hooks": {"Stop": [{"hooks": [{"type": "command",
#       "command": "sh /path/to/this/repo/scripts/autosync.sh", "async": true, "timeout": 20}]}]}
#
# List your repos here. Add "push" for a repo without its own post-commit push
# (for example ~/.claude/scheduled-tasks turned into a repo with `git init`).
REPOS="$HOME/Developer/claude-skills-starter
$HOME/.claude/scheduled-tasks push"

LOG="$HOME/.claude/hooks/state/auto-sync.log"
mkdir -p "$(dirname "$LOG")" 2>/dev/null
echo "$REPOS" | while read -r DIR MODE; do
  [ -d "$DIR/.git" ] || continue
  cd "$DIR" || continue
  [ -z "$(git status --porcelain 2>/dev/null)" ] && continue
  CHANGED=$(git status --porcelain | awk '{print $2}' | head -8 | tr '\n' ' ')
  git add -A >/dev/null 2>&1
  if git commit -q -m "Auto-sync $(date '+%Y-%m-%d %H:%M'): $CHANGED" >>"$LOG" 2>&1; then
    [ "$MODE" = "push" ] && git push -q origin HEAD >>"$LOG" 2>&1
    echo "$(date '+%F %T') synced $DIR: $CHANGED" >>"$LOG"
  else
    git reset -q >/dev/null 2>&1
    echo "$(date '+%F %T') commit stopped in $DIR, left uncommitted" >>"$LOG"
  fi
done
exit 0

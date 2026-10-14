#!/bin/sh
# End-of-turn auto-sync. Commits and pushes any uncommitted change in the repos below, so an edit
# made by Claude (or by you) is backed up and reaches every surface without a manual commit.
#
# Install as a Claude Code Stop hook in ~/.claude/settings.json:
#   "hooks": {"Stop": [{"hooks": [{"type": "command",
#       "command": "sh /path/to/this/repo/scripts/autosync.sh", "async": true, "timeout": 20}]}]}
#
# List your repos here, one per line: your skills repo first. Add "push" after a repo that has no
# post-commit hook of its own, for example ~/.claude/scheduled-tasks once you've turned it into a repo
# with `git init`. That line ships commented out, so the script never touches your routines unless
# you add them on purpose.
REPOS="$HOME/Developer/YOUR-SKILLS-REPO"
# REPOS="$REPOS
# $HOME/.claude/scheduled-tasks push"

LOG="$HOME/.claude/hooks/state/auto-sync.log"
mkdir -p "$(dirname "$LOG")" 2>/dev/null
case "$REPOS" in *YOUR-SKILLS-REPO*)
  echo "$(date '+%F %T') autosync.sh: set REPOS to your skills repo folder, nothing synced" >>"$LOG"
  echo "autosync.sh: edit REPOS at the top of this script first" >&2; exit 1;;
esac
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

#!/usr/bin/env python3
"""Deterministic skill triggers.

A skill's description only fires when the model happens to match it. For the skills you want to
fire every time (a check before building, a voice pass before drafting), this hook matches your prompt
against the patterns in nudges.json and adds one line of context naming the skill to run.

UserPromptSubmit: one line per matching rule.
PreToolUse Write: the first NEW code file of MIN_LINES+ lines in a session is held once, unless the
  "before_new_code" skill already ran this session. Re-issuing the same Write goes through.

Edit nudges.json, not this file. Never fails the caller: internal errors exit 0.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.expanduser("~/.claude/hooks/state")
CODE_EXT = (".py", ".js", ".mjs", ".ts", ".tsx", ".jsx", ".sh", ".go", ".rs", ".rb", ".swift", ".java", ".kt")


def load():
    with open(os.path.join(HERE, "nudges.json")) as f:
        return json.load(f)


def skill_loaded(transcript, name):
    try:
        with open(transcript, encoding="utf-8", errors="ignore") as f:
            return any(name in l and ('"Skill"' in l or "Base directory for this skill" in l) for l in f)
    except (OSError, TypeError):
        return False


def main():
    d = json.load(sys.stdin)
    cfg = load()
    event = d.get("hook_event_name")
    if event == "UserPromptSubmit":
        lines = [f"Standing pull: {r['skill']}. {r['action']}, or say in one clause why it does not apply."
                 for r in cfg.get("prompt_rules", []) if re.search(r["pattern"], d.get("prompt", ""), re.I)]
        if lines:
            print("\n".join(lines))
        return
    gate = cfg.get("before_new_code")
    if event == "PreToolUse" and d.get("tool_name") == "Write" and gate:
        ti = d.get("tool_input", {})
        path, content = ti.get("file_path", ""), ti.get("content", "")
        if (not path.endswith(CODE_EXT) or os.path.exists(path) or path.startswith(("/tmp/", "/private/tmp/"))
                or content.count("\n") < gate.get("min_lines", 80)
                or skill_loaded(d.get("transcript_path", ""), gate["skill"])):
            return
        os.makedirs(STATE, exist_ok=True)
        marker = os.path.join(STATE, f"new-code-{d.get('session_id', 'x')}")
        if os.path.exists(marker):
            return
        open(marker, "w").write(path)
        print(f"Gate: {os.path.basename(path)} is a new {content.count(chr(10))}-line code file and "
              f"{gate['skill']} has not run this session. {gate['action']} Then re-issue this same Write.",
              file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        pass
    sys.exit(0)

#!/usr/bin/env python3
"""Run the house voice's mechanical rules (Vale, HouseVoice style) on text Claude writes.

Wired by this plugin's hooks/hooks.json:
  PreToolUse  email draft/send tools (Composio Gmail, Gmail connector) -> exit 2 blocks until clean
  PostToolUse Write/Edit/MultiEdit on .md/.html/.txt, Notion page writes -> reports hits back to Claude

The rules live with the voice skill (skills/house-voice/vale/ in this plugin). Judgment rules stay in the
skill's SKILL.md. Skips: email subjects, headings and code (Vale scopes), any text or file containing
"voice-check: off", and Vale's own <!-- vale off --> ... <!-- vale on --> blocks.
Never fails the caller: any internal error exits 0 silently.
"""
import json, os, re, subprocess, sys, tempfile

VOICE_SKILL = "house-voice"   # the skill whose vale/ folder holds the rules, and that must load before an email
VALE = os.environ.get("VALE_BIN", "vale")   # Vale on PATH, or set VALE_BIN
CFG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skills", VOICE_SKILL, "vale", ".vale.ini")
OFF = "voice-check: off"

EMAIL_SLUGS = {"GMAIL_CREATE_EMAIL_DRAFT", "GMAIL_UPDATE_DRAFT", "GMAIL_SEND_EMAIL",
               "GMAIL_REPLY_TO_THREAD", "GMAIL_SEND_DRAFT", "GMAIL_FORWARD_MESSAGE"}
BODY_KEYS = ("body", "html_body", "htmlBody", "text", "message", "content", "plain_text")
PROSE_EXT = (".md", ".html", ".txt")
SKIP_PATHS = ("/node_modules/", "/.git/", "/private/tmp/", "/tmp/", "/vale/styles/")


STATE = os.path.expanduser("~/.claude/hooks/state")


def voice_loaded(transcript):
    try:
        with open(transcript, encoding="utf-8", errors="ignore") as f:
            return any(VOICE_SKILL in l and ('"Skill"' in l or "Base directory for this skill" in l)
                       for l in f)
    except (OSError, TypeError):
        return False


def lint(text, ext):
    """Return (errors, warnings) as lists of 'line N: message' strings."""
    if not text or not text.strip() or OFF in text:
        return [], []
    with tempfile.NamedTemporaryFile("w", suffix=ext, delete=False) as f:
        f.write(text)
        path = f.name
    try:
        out = subprocess.run([VALE, "--config", CFG, "--output", "JSON", path],
                             capture_output=True, text=True, timeout=20).stdout
    finally:
        os.unlink(path)
    alerts = next(iter(json.loads(out or "{}").values()), [])
    errs, warns = [], []
    for a in alerts:
        (errs if a["Severity"] == "error" else warns).append(
            f"line {a['Line']}: \"{a['Match']}\" -> {a['Message']}")
    return errs, warns


def ext_for(text):
    return ".html" if re.search(r"<(p|div|br|ul|li|h\d)\b", text or "", re.I) else ".md"


def email_bodies(name, tool_input):
    """Yield body strings from an email-sending tool call (subjects are skipped on purpose)."""
    if name.endswith("COMPOSIO_MULTI_EXECUTE_TOOL"):
        for t in tool_input.get("tools", []):
            if t.get("tool_slug") in EMAIL_SLUGS:
                args = t.get("arguments", {})
                for k in BODY_KEYS:
                    if isinstance(args.get(k), str):
                        yield args[k]
    else:  # Gmail connector: create_draft, update_draft, reply, send_message, forward
        for k in BODY_KEYS:
            if isinstance(tool_input.get(k), str):
                yield tool_input[k]


def notion_texts(tool_input):
    for p in tool_input.get("pages", []) or []:
        if isinstance(p.get("content"), str):
            yield p["content"]
    for u in tool_input.get("content_updates", []) or []:
        if isinstance(u.get("new_str"), str):
            yield u["new_str"]
    for k in ("content", "new_str"):
        if isinstance(tool_input.get(k), str):
            yield tool_input[k]


def file_texts(name, tool_input):
    path = tool_input.get("file_path", "")
    if not path.endswith(PROSE_EXT) or any(s in path for s in SKIP_PATHS) or path.endswith("MEMORY.md"):
        return path, []
    try:
        if OFF in open(path, encoding="utf-8", errors="ignore").read():
            return path, []
    except OSError:
        pass
    if name == "Write":
        return path, [tool_input.get("content", "")]
    if name == "Edit":
        return path, [tool_input.get("new_string", "")]
    return path, [e.get("new_string", "") for e in tool_input.get("edits", [])]


def report(errs, warns, where):
    lines = [f"Voice check ({where}), house voice rules:"]
    lines += [f"  ERROR {e}" for e in errs] + [f"  warn  {w}" for w in warns]
    return "\n".join(lines)


def main():
    data = json.load(sys.stdin)
    event, name, ti = data.get("hook_event_name"), data.get("tool_name", ""), data.get("tool_input", {})
    errs, warns = [], []

    if event == "PreToolUse":  # outbound email: voice skill loaded, then block until clean
        bodies = list(email_bodies(name, ti))
        if bodies and not voice_loaded(data.get("transcript_path", "")):
            marker = os.path.join(STATE, f"voice-{data.get('session_id', 'x')}")
            if not os.path.exists(marker):
                os.makedirs(STATE, exist_ok=True)
                open(marker, "w").write("held")
                print("Voice gate: " + VOICE_SKILL + " has not loaded this session. Load it with the Skill tool, "
                      "apply its judgment rules to this email, then resend the same call.", file=sys.stderr)
                sys.exit(2)
        for body in bodies:
            e, w = lint(body, ext_for(body))
            errs += e
            warns += w
        if errs:
            print(report(errs, warns, "email draft blocked") +
                  "\nFix these in the body and resend the same call. Subject lines are not checked. "
                  f"If the author explicitly wants the text as written, add the HTML comment <!-- {OFF} --> to the body.",
                  file=sys.stderr)
            sys.exit(2)
        sys.exit(0)

    if event == "PostToolUse":
        if "notion" in name:
            where = "Notion page"
            texts = list(notion_texts(ti))
            ext = ".md"
        else:
            where, texts = file_texts(name, ti)
            ext = os.path.splitext(where)[1] or ".md"
        for t in texts:
            e, w = lint(t, ext)
            errs += e
            warns += w
        if errs:
            print(json.dumps({"decision": "block", "reason": report(errs, warns, where) +
                              "\nFix the ERROR lines now (they already landed). Warnings are judgment calls."}))
        elif warns:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                              "additionalContext": report(errs, warns, where)}}))
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)

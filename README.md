# Claude skills starter

One GitHub repo for every Claude skill you write. Claude Code, claude.ai and Cowork all install from it and update themselves when you push, so there are no more `.skill` uploads and no more copies drifting apart.

Built by [Serious AI](https://seriousai.partners) from the setup we run ourselves: 63 skills in six plugins, one repo. On the day we consolidated, twelve of our skills had edits that had never reached claude.ai, and nothing showed it until we compared every copy. This template is the setup, minus our skills.

## What you get

- **A plugin marketplace skeleton:** `.claude-plugin/marketplace.json` and one plugin, `plugins/my-skills/`, with two working example skills:
  - `house-voice`: a writing voice, with its mechanical rules enforced by a check rather than remembered
  - `build-check`: search for an existing tool before building a new one
- **Versions that bump themselves.** Installed plugins only update when the version moves. The pre-commit hook raises the patch version of every plugin that changed and validates the manifests. The post-commit hook pushes.
- **Rules that hold every run.** The `house-voice` skill ships a [Vale](https://vale.sh) style (a free, open-source prose linter). A hook in the plugin blocks outbound email drafts that break the rules, and flags them in files and Notion pages.
- **Skills that fire when they should.** A skill's description only fires when the model happens to match it. `hooks/nudges.json` maps prompt patterns to the skill that should run, and holds the first new 80+ line code file of each session until `build-check` has run.
- **End-of-turn auto-sync.** `scripts/autosync.sh` commits and pushes any uncommitted change after every Claude turn, for this repo and for your scheduled routines if you put them in git too.

## Quick start

1. **Use this template** (the green button on GitHub) to make your own copy. Keep it private if your skills hold anything you wouldn't publish.
2. Clone it, then turn on the git hooks: `git config core.hooksPath .githooks`.
3. Rename `my-skills` in `.claude-plugin/marketplace.json` and `plugins/my-skills/.claude-plugin/plugin.json` to your own name, and put your skills in `plugins/my-skills/skills/<skill-name>/SKILL.md`. Add more plugins as folders under `plugins/` to group skills you'll want to switch off together.
4. Install Vale for the voice check: `brew install vale` (or see vale.sh for other platforms). Edit the rules in `plugins/my-skills/skills/house-voice/vale/styles/HouseVoice/`.
5. Validate and push: `claude plugin validate .` and `claude plugin validate plugins/my-skills`, then commit (the hooks bump the version and push).
6. **Claude Code:** `claude plugin marketplace add <you>/<repo>`, then `claude plugin install my-skills@my-skills`. Turn on auto-update with `/plugin`, Marketplaces, your marketplace, Enable auto-update (interactive terminal).
7. **claude.ai, desktop chat and Cowork:** in the desktop app, open a **Chat** conversation (not the Code tab), then Customize, Plugins, Add marketplace, `<you>/<repo>`. Connect GitHub if the repo is private. Then open **Discover** and install your plugins.
8. **Clean up:** delete your old uploaded copies under Customize, Skills, "Created by you", and any local copies in `~/.claude/skills`. Install first, delete second.
9. **Optional auto-sync:** add `scripts/autosync.sh` as a Claude Code Stop hook (instructions at the top of the script).

## The traps, and the fix for each

1. **Installs don't update unless the version moves.** The pre-commit hook bumps it for you.
2. **A `github` marketplace source clones over SSH.** With no SSH key for GitHub, installing a plugin from another repo fails with a host-key error. Use `{"source": "url", "url": "https://github.com/owner/repo.git"}`.
3. **The Code tab's Customize screen is your local Claude Code, not your account.** Adding the marketplace there errors if the CLI already has it. Add it from a Chat conversation.
4. **Adding a marketplace installs nothing.** Its plugins wait under Discover. The "Yours" tab only lists installed plugins, so it looks empty.
5. **Skills get a plugin prefix** (`my-skills:house-voice`). Anything that names a skill by its bare name needs a look.
6. **Hooks only run in Claude Code.** claude.ai and Cowork load the same skills without the enforcement.
7. **A folder in `~/.claude/skills` that contains `.claude-plugin/plugin.json` becomes a local plugin.** Remove local copies once the marketplace install works, or skills show twice.
8. **Claude Code's safety check stops Claude from rewiring its own skill folders and settings.** Run the install commands yourself.
9. **Old uploads keep running alongside the plugins** until you delete them.
10. **Every installed skill's description loads on every turn.** Keep a large third-party library in its own plugin so you can switch it off.

## Layout

```
.claude-plugin/marketplace.json      the marketplace: lists your plugins
.githooks/pre-commit                 bumps changed plugins' versions, validates
.githooks/post-commit                pushes main in the background
scripts/autosync.sh                  optional Stop hook: commit and push after every Claude turn
plugins/my-skills/
  .claude-plugin/plugin.json         name, version, description
  hooks/hooks.json                   wires the hooks below into Claude Code
  hooks/voice_check.py               runs the Vale rules on email drafts, files and Notion writes
  hooks/nudges.py + nudges.json      prompt patterns that name the skill to run
  skills/house-voice/                example skill, with vale/ rules
  skills/build-check/                example skill
```

## License

MIT. Use it, change it, ship it. If it saves you an afternoon, [tell us](https://seriousai.partners).

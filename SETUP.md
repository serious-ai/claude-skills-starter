# Guided setup (Claude reads this)

The person asked you to set this template up for them. Most people asking have never used git hooks, a plugin marketplace or a terminal much, so you do the technical work and they do only what needs their hands. Walk them through it one step at a time. Before each step, say in one plain sentence what it does and why. After each step, confirm it worked before moving on.

Two kinds of step:

- **You run it.** Run the command yourself and report the result in plain words.
- **They do it.** Claude Code's safety rules stop you from installing plugins into yourself, and only they can click in the desktop app. Give them the exact command to paste, or the exact clicks, one at a time, then wait for them to say it's done.

## 0. Check the tools

Check that `git`, `gh` (the GitHub command-line tool) and `claude` are installed, and that `gh auth status` shows them signed in. If `gh` is missing, have them install it (`brew install gh` on a Mac) and run `gh auth login` themselves, since it opens a browser sign-in. Vale, the writing-style checker, is optional: offer `brew install vale`.

Then ask three questions in one message, each with your suggestion:

1. **Repo name?** Suggest `claude-skills`.
2. **Private or public?** Suggest private, since skills often hold client names and house methods.
3. **Plugin name?** That's the label the skills install under. Suggest their first name or company name, lowercase with dashes.

Done when the three tools work and the three answers are in.

## 1. Make their copy

Run `gh repo create <repo> --template serious-ai/claude-skills-starter --private --clone` (or `--public`), in a folder they'll remember, such as `~/Developer`. Then `cd` into it and run `git config core.hooksPath .githooks`, which turns on the two automatic scripts: one raises the version number before each save, and one sends each save up to GitHub through a pull request that merges itself.

Done when the folder exists and `git config core.hooksPath` prints `.githooks`.

## 2. Make it theirs

Rename `my-skills` to their plugin name in `.claude-plugin/marketplace.json` (both the marketplace `name` and the plugin `name` and `source`), in `plugins/my-skills/.claude-plugin/plugin.json`, and the folder itself (`git mv plugins/my-skills plugins/<name>`). Put their name in the `owner` and `author` fields. Point `REPOS` in `scripts/autosync.sh` at the new folder.

Done when `grep -r my-skills .` (outside `.git`) only finds README mentions.

## 3. Bring in their skills

Find every skill they already have:

- folders in `~/.claude/skills/` and any project's `.claude/skills/`
- skills that exist only on claude.ai: ask them to open each one under Customize, Skills and download it, or paste its content to you

Copy each skill folder into `plugins/<name>/skills/<skill-name>/`. When two copies of one skill differ, keep the one with the newest content, not the newest file date, since copying resets dates. Ask before keeping both. Read every file of any skill someone else wrote before it goes in.

Done when every skill they named is in the repo and they've confirmed the list.

## 4. Save it to GitHub

Run `claude plugin validate .` and `claude plugin validate plugins/<name>`, and fix anything they report. Then commit on `main`. Wait about 20 seconds and read `.git/last-push.log`: it should say `merged` with a pull request link.

Done when the log says `merged` and `git status -sb` shows nothing ahead or behind.

## 5. Install it in Claude Code (they do it)

Give them these commands to paste into their own terminal:

```
claude plugin marketplace add <github-user>/<repo>
claude plugin install <name>@<name>
```

Then have them type `/plugin` in Claude Code, open Marketplaces, choose theirs and turn on auto-update.

Done when `claude plugin list` shows their plugin.

## 6. Install it on claude.ai and Cowork (they do it)

Coach these clicks one at a time:

1. In the Claude desktop app, open a **Chat** conversation. The Code tab's Customize screen is the local install, so the marketplace has to be added from Chat.
2. Customize, then Plugins, then Add marketplace. Enter `<github-user>/<repo>`. If the repo is private, connect GitHub when asked.
3. Adding a marketplace installs nothing yet. Open **Discover** and install their plugin.

Done when they can see the plugin under Plugins with its skills listed.

## 7. Remove the old copies

Only after steps 5 and 6 work: have them delete their old uploads under Customize, Skills, "Created by you". Move (don't delete) the old folders out of `~/.claude/skills/` into a backup folder, so each skill shows up once.

Done when each skill appears once.

## 8. Optional: save automatically after every turn

Offer to add `scripts/autosync.sh` as a Claude Code Stop hook (the instructions are at the top of the script). With it, any edit Claude makes to a skill is saved and sent up without anyone typing a commit. Add it only on their yes.

## Finish

Tell them in three lines what they now have: one place where their skills live, every Claude surface installing from it, and updates that land without uploads. Then the one habit that keeps it working: edit skills only in this repo. Point them at the README's "The traps" section for anything that looks odd later.

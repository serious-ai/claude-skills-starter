# Teams and organizations

The same setup for a company on Claude Team or Enterprise: one repo holds the company's skills, each team gets its own plugin, and the people who own a team's skills approve every change to them. The files in this folder are examples to copy into your company repo.

## Layout

```
acme/claude-skills (private)             the company marketplace
  .claude-plugin/marketplace.json        lists every plugin (see the example here)
  .github/CODEOWNERS                     who approves changes to each plugin
  plugins/company/                       everyone: house voice, build check, glossary
  plugins/sales/                         sales team
  plugins/ops/                           operations team
acme/claude-skills-finance (private)     a team whose skills only it may see
```

**One plugin per team** is the unit people install and switch off. Put company-wide skills in `company`, and give each team its own plugin so members only carry the skills that apply to them. Every installed skill's description sits in context on every turn, so this also keeps each person's context lean.

## Who can see what

GitHub permissions are per repo, not per folder. Anyone who can read the company repo can read every plugin in it.

- **Skills anyone in the company may see** go in the company repo.
- **Skills only one team may see** go in that team's own private repo, listed in the company marketplace with a `url` source (see `finance` in the example). Members without access to that repo can't install it, because each person's install clones with their own GitHub credentials.
- Everyone who installs needs GitHub read access to the repos they install from.

## Who can change what

Copy `.github/CODEOWNERS`, then turn on branch protection for `main` with "require review from Code Owners". A change to the sales plugin then needs a sales lead's approval before it reaches anyone. That review is the check that keeps a shared skill from drifting or quietly breaking for a whole team.

## Rolling it out

**Claude Code (confirmed in Anthropic's docs):** an admin can register the marketplace and switch plugins on for the whole organization through managed settings, under Organization settings, Claude Code, Managed settings, or through a `managed-settings.json` file deployed to machines. `managed-settings.example.json` here registers the company marketplace, turns on the `company` plugin for everyone, and allows only that marketplace. Managed settings apply to the whole organization. For team-specific defaults, deploy a different managed settings file to each team's machines, or let each member install their team's plugin themselves.

**claude.ai, desktop chat and Cowork:** each member adds the marketplace from a Chat conversation (Customize, Plugins, Add marketplace), then installs `company` and their team's plugin from Discover. Whether an admin can push plugins to these surfaces for the whole organization varies by plan and was not confirmed in the docs as of September 30, 2026. Check your admin console.

## Routines

Scheduled routines run on one person's machine (desktop scheduled tasks) or in the cloud (Claude Code routines). There is no built-in way to share a routine across people. Keep each team's routines in a `routines/<team>/` folder in the company repo as the reviewed source, and have each owner install theirs locally. Put a personal routines folder in git on each machine with the `scripts/autosync.sh` pattern.

## Keep in the repo root

The same `.githooks/` as the personal template: every commit bumps the version of each plugin that changed and validates the manifests, so a merged change reaches every member on their next sync.

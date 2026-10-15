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
- Everyone who installs through Claude Code or their own claude.ai account needs GitHub read access to the repos they install from. Plugins an Owner syncs into the organization (see Rolling it out) reach members without it.

## Who can change what

Copy `.github/CODEOWNERS`, then turn on branch protection for `main` with "require review from Code Owners". A change to the sales plugin then needs a sales lead's approval before it reaches anyone. That review is the check that keeps a shared skill from drifting or quietly breaking for a whole team.

The same goes for a skill someone finds or downloads: it arrives as a pull request into the right team's plugin, gets read file by file and approved by that plugin's owner, and only then reaches anyone. Nobody installs skills through the desktop app's install button, which would put an unreviewed copy on one person's account.

## Rolling it out

**Claude Code (confirmed in Anthropic's docs):** an admin can register the marketplace and switch plugins on for the whole organization through managed settings, under Organization settings, Claude Code, Managed settings, or through a `managed-settings.json` file deployed to machines. `managed-settings.example.json` here registers the company marketplace, turns on the `company` plugin for everyone, and allows only that marketplace. Managed settings apply to the whole organization. For team-specific defaults, deploy a different managed settings file to each team's machines, or let each member install their team's plugin themselves.

**claude.ai, desktop chat and Cowork (confirmed in Anthropic's docs, October 15, 2026):** an Owner on a Team or Enterprise plan adds the company repo under Organization settings, Plugins & skills, Add, Sync from GitHub (or Sync from GitLab). Members then receive the plugins without needing access to the repository themselves. Turn on Sync automatically and every merge to `main` reaches members, which makes the code-owner review above the one gate a change passes. Then set each plugin's Default access: Not available, Available to install, Installed by default, or Required (members can't turn a required plugin off). On Enterprise, Group access gives a plugin its own setting per user group, so the sales plugin can install for the sales group only. Team plans have no group setting: install `company` for everyone and let members install their team's plugin from Discover. The Policy tab can also switch off member-created skills and set publishing to Requires review, so nothing reaches the organization without an approval. Guide: https://claude.com/docs/plugins/admin

**Which skills people actually use:** the Inventory tab's Users (30d) column shows how many people used each plugin and skill in the last 30 days. Sort by Most users to find the skills nobody runs, and retire them. Every installed skill's description costs context on every turn, and once the listing passes its budget (1% of the context window) Claude Code drops descriptions starting with the least-used skills, which removes the keywords Claude needs to match a request. A sprawling library loses exactly the skills people call rarely. Details: https://code.claude.com/docs/en/skills (Skill descriptions are cut short).

## Routines

Scheduled routines run on one person's machine (desktop scheduled tasks) or in the cloud (Claude Code routines). There is no built-in way to share a routine across people. Keep each team's routines in a `routines/<team>/` folder in the company repo as the reviewed source, and have each owner install theirs locally. Put a personal routines folder in git on each machine with the `scripts/autosync.sh` pattern.

## Keep in the repo root

The same `.githooks/` as the personal template: every commit bumps the version of each plugin that changed and validates the manifests, so a merged change reaches every member on their next sync.

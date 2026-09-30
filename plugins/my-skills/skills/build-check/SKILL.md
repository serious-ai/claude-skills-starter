---
name: build-check
description: Build check before writing non-trivial new code. Search GitHub, package registries and published skill libraries for something that already does it, so you fork or install instead of rebuilding. Fires on a request for a new tool, script, integration, pipeline, bot, automation or skill, and when Claude is about to create a new code file of about 50+ lines. Skips tiny one-off scripts and work already mid-build.
---

# Build check (example skill)

A few minutes of search beats hours of tokens rebuilding a solved problem.

1. **Name the capability in plain terms:** what it has to do, not how you'd build it.
2. **Search, 2 or 3 queries, then stop:** GitHub (the capability plus "cli", "self-hosted", "awesome"), the package registry for your language, and for agent skills or engineering process, published skill libraries such as github.com/anthropics/skills and github.com/mattpocock/skills.
3. **Judge a candidate on fit first, then maintenance** (recent commits, open issues), **then license** (MIT, Apache and BSD are the easy cases, and GPL or AGPL needs a decision).
4. **Report in one line:** a fit (link it, say why, recommend installing or forking), a partial fit (what it covers and what's missing), or nothing found. Nothing found is a fine, fast result. Then build.

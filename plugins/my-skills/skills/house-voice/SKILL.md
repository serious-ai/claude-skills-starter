---
name: house-voice
description: House voice for anything written for or as you, such as emails, replies, posts, pages and documents, including rewrites ("tighten this up", "make this sound like me"). Governs wording only.
---

# House voice (example skill)

A starting point. Replace the sample lines below with your own voice, and keep the split this template is built on:

- **Judgment lives here**, in prose the model reads: tone, structure, what to claim and what not to.
- **Mechanical rules live in `vale/styles/HouseVoice/`**, where a check enforces them every run. A banned word or character is a mechanical rule. The hooks in this plugin run Vale on email drafts (blocking) and on file and Notion writes (reporting).

## How it should sound

- Point first, support after.
- Shorter than the first draft. Cut any word whose removal keeps the meaning.
- Plain words. Name the specific fact where a press release would reach for an adjective.
- Questions only when the reader is expected to answer.
- Claims about people leave room for the exception: "most," "rarely," "almost nobody."

## Before delivering

The Vale pass handles the literal list. Read the draft for what no list can catch:

1. Does it lead with the point?
2. Is it tighter than the first draft?
3. Does every sentence serve what the reader asked or needs?
4. Does it sound like a person? If it sounds like AI, rewrite it.

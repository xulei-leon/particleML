---
name: feedback-no-coauthor-in-commits
description: "Do not include \"Co-Authored-By\" trailer in commit messages"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 194c3471-b515-4174-95d5-0c4835f63691
---

Do not add "Co-Authored-By: Claude ... <noreply@anthropic.com>" or any "Co-Authored-By" trailer to commit messages.

**Why:** The user explicitly requested this after seeing it in an initial commit.

**How to apply:** When creating git commits, omit the "Co-Authored-By" trailer entirely. Keep commit messages clean with just the subject line and body.

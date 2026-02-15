---
description: "Record errors after bugfix, failed deploy, or 2+ failed attempts to prevent recurrence"
---

# Error Learning

After a bugfix, failed deploy, or 2+ failed attempts at a task:

1. **Record** in `.claude/data/error-log.md`:
   - Symptom (what happened)
   - Root Cause (why — dig past the surface)
   - Fix (what was done)
   - Prevention (what to update so this doesn't repeat)
   - Files (affected)

2. **Update instructions** if the error reveals a gap:
   - CLAUDE.md — if it's a project-wide pattern
   - Memory (MEMORY.md) — if it's a cross-session insight
   - Skip if the error is one-off and unlikely to repeat

3. **Rule of Three**: update instructions immediately on first occurrence only if the fix is obvious. Otherwise wait for 3 occurrences of the same class of error before codifying a rule.

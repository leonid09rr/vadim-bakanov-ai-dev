---
status: planned
depends_on: []
wave: 1
---

# Task N: {Name}

## Description
What we're doing and why. Context from tech-spec.

## What to do
Concrete steps — WHAT, not HOW. Not pseudocode.

## TDD Anchor
Tests to write BEFORE implementation:
- `tests/test_xxx.py::test_create_user` — POST /api/users creates user, returns 201
- `tests/test_xxx.py::test_create_user_duplicate` — POST with existing email -> 409

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Context Files
- [user-spec.md](../user-spec.md)
- [tech-spec.md](../tech-spec.md)

## Verification Steps

### Automated
- `pytest tests/test_xxx.py -v` -> all pass

### Smoke
- `curl -X POST localhost:3000/api/users -d '{"name":"test"}' -H 'Content-Type: application/json'` -> 201

## Details
**Files:** path/to/file.ts — what to do
**Dependencies:** other tasks, packages
**Edge cases:** list

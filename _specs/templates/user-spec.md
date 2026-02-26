---
created: YYYY-MM-DD
status: draft
type: feature
size: S
---

# User Spec: {Feature Name}

## What we're doing
{2-3 sentences: the essence of the feature/fix}

## Why
{What problem are we solving / what value are we delivering}

## How it should work
{User scenario in free form:
1. User does X
2. System responds with Y
3. Result is Z}

## Acceptance Criteria
- [ ] {Criterion 1 - what should work}
- [ ] {Criterion 2}
- [ ] {Criterion 3}

## Constraints
{Technical and business constraints: compatibility, security, scalability}

## Risks
- **Risk 1:** {description}. **Mitigation:** {action}.

## Technical Decisions
- We decided to {do X} because {Y}.
- We decided to {not do Z} because {W}.

## Testing

**Unit tests:** always, non-negotiable.
**Integration tests:** {yes/no} — {reason}.
**E2E tests:** {yes/no} — {reason}.

## How to verify

### Agent verifies

| Step | Tool | Expected Result |
|------|------|-----------------|
| {1. Description} | {curl / bash / MCP} | {What should happen} |

### User verifies
- {What to check — how to check — why manual check is needed}

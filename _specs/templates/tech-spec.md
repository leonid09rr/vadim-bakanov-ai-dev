---
created: YYYY-MM-DD
status: draft
branch: dev
size: S
---

# Tech Spec: {Feature Name}

## Solution
Technical approach description.

## Architecture

### What we're building/modifying
- **Component A** — purpose
- **Component B** — purpose

### How it works
Data flow, interactions, sequence.

### Shared resources

| Resource | Owner (creates) | Consumers | Instance count |
|----------|----------------|-----------|----------------|
| {example: DB pool} | {main.py} | {Service A, Service B} | {1 (singleton)} |

## Decisions

### Decision 1: {topic}
**Decision:** what we chose
**Rationale:** why
**Alternatives considered:** what else, why rejected

## Data Models
DB schemas, interfaces, types. Skip if N/A.

## Dependencies

### New packages
- `package-name` — purpose

### Using existing (from project)
- `module-name` — how

## Testing Strategy

### Unit tests
- Scenario 1: what we test
- Scenario 2: ...

### Integration tests
- Scenario 1 (if M/L feature)
- "None" (if S feature)

## Risks

| Risk | Mitigation |
|------|-----------|
| Risk 1 | What we do |

## Acceptance Criteria
- [ ] All tests pass (unit, integration if applicable)
- [ ] No regressions in existing tests
- [ ] {Additional technical criteria}

## Implementation Tasks

### Wave 1 (independent)

#### Task 1: {Name}
- **Description:** {What and why}
- **Files to modify:** `src/...`
- **Files to read:** `src/...`
- **Verify-smoke:** `curl ...` -> expected result

### Wave 2 (depends on Wave 1)

#### Task 2: {Name}
- **Description:** {What and why}
- **Files to modify:** `src/...`

### Final Wave

#### Task N: QA
- **Description:** Run all tests, verify acceptance criteria

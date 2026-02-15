# System Architecture — Claude Code Workspace

Last Updated: 2026-02-15

---

## 1. High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        WORKSPACE ROOT                               │
│                                                                     │
│   CLAUDE.md ◄── Single Source of Truth for AI assistant             │
│   VERSION        Semantic versioning (0.0.1)                        │
│   .gitignore     Security: no .env, no credentials                  │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────────┐  │
│  │  .claude/    │  │  src/        │  │  Infrastructure           │  │
│  │              │  │  (your code) │  │                           │  │
│  │  AI Brain    │  │              │  │  _status/    environments │  │
│  │  Skills      │  │  tests/      │  │  _changelogs/ releases   │  │
│  │  Agents      │  │  (your tests)│  │  _specs/      specs      │  │
│  │  Rules       │  │              │  │  backlog/     tasks       │  │
│  │  Data        │  │  scripts/    │  │  documentation/ docs     │  │
│  │  Settings    │  │  (your tools)│  │                           │  │
│  └──────┬───────┘  └──────────────┘  └───────────────────────────┘  │
│         │                                                           │
│         ▼                                                           │
│  Claude Code reads .claude/ + CLAUDE.md on every session start      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. .claude/ — AI Brain Structure

```
.claude/
│
├── settings.json          ◄── Permissions + Hooks (auto ruff on .py)
├── settings.local.json    ◄── Personal overrides (gitignored)
│
├── rules/                 ◄── Auto-triggered behaviors
│   ├── error-learning.md      Fires: after bugfix / failed deploy / 2+ failures
│   └── auto-backup.md        Fires: after 3+ files changed / task complete
│
├── agents/                ◄── Specialized sub-processes (delegated by Claude)
│   ├── deployer.md            9-step deploy with safety checks
│   ├── docs-generator.md      Updates 3 status files post-deploy
│   └── test-runner.md         5-phase testing pipeline
│
├── skills/                ◄── User-invoked slash commands (/command)
│   ├── README.md              Skill catalog
│   ├── commit/SKILL.md        /commit
│   ├── push/SKILL.md          /push
│   ├── cherry-pick/SKILL.md   /cherry-pick
│   ├── merge-to-prod/SKILL.md /merge-to-prod
│   ├── git-status/SKILL.md    /git-status
│   ├── deploy-dev/SKILL.md    /deploy-dev
│   ├── deploy-prod/SKILL.md   /deploy-prod
│   ├── test/SKILL.md          /test
│   ├── docs/SKILL.md          /docs
│   ├── techdebt/SKILL.md      /techdebt
│   ├── architect/SKILL.md     /architect
│   └── project-manager/       /project-manager
│       ├── SKILL.md
│       └── references/
│           └── role.md        PM role definition
│
└── data/                  ◄── Persistent AI memory
    └── error-log.md           Structured error history
```

---

## 3. Skills vs Agents vs Rules

```
┌─────────────────────────────────────────────────────────────────┐
│                    HOW THEY DIFFER                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SKILLS (12)              AGENTS (3)            RULES (2)       │
│  ─────────────            ──────────            ─────────       │
│  User-invoked             Claude-delegated      Auto-triggered  │
│  /command                 Task tool             Pattern match   │
│                                                                 │
│  ┌─────────┐              ┌─────────┐          ┌─────────┐     │
│  │  User   │─── /cmd ───▶│  Claude  │──delegate─▶│ Claude │     │
│  │         │              │  (main) │          │ (agent) │     │
│  └─────────┘              └────┬────┘          └─────────┘     │
│                                │                                │
│                                │ auto                           │
│                                ▼                                │
│                           ┌─────────┐                           │
│                           │  Rule   │                           │
│                           │ triggers│                           │
│                           └─────────┘                           │
│                                                                 │
│  Examples:                Examples:             Examples:        │
│  /commit                  deployer              error-learning   │
│  /deploy-prod             docs-generator        auto-backup      │
│  /project-manager         test-runner                            │
│                                                                 │
│  Trigger: explicit        Trigger: Claude       Trigger: event   │
│  Format: SKILL.md         Format: agent.md      Format: rule.md  │
│  Can have: references/    Has: tools, model     Has: description │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Skills Map — 12 Commands by Category

```
┌─────────────────────────────────────────────────────────────────┐
│                      SKILLS CATALOG                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  GIT & CI/CD                                                    │
│  ──────────                                                     │
│  /commit ─────── AI commit message (conventional commits)       │
│  /push ───────── Safe push with preview + confirmation          │
│  /cherry-pick ── Transfer: local → dev                          │
│  /merge-to-prod  Transfer: dev → prod (requires confirmation)   │
│  /git-status ─── Multi-branch overview                          │
│  /deploy-dev ─── Deploy to DEV environment                      │
│  /deploy-prod ── Deploy to PROD (safety checklist)              │
│                                                                 │
│  QUALITY                                                        │
│  ───────                                                        │
│  /test ───────── lint → types → unit → build                    │
│  /techdebt ───── TODO/FIXME scan, large files, outdated deps    │
│                                                                 │
│  DOCS & PLANNING                                                │
│  ───────────────                                                │
│  /docs ───────── Update _status/ + changelogs after deploy      │
│  /architect ──── Design features (components, models, plan)     │
│  /project-manager  Backlog, sprints, priorities                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Git Workflow — Three-Branch Strategy

```
                        ┌──────────────────────────┐
                        │      Git Branches         │
                        └──────────────────────────┘

    local (working)          dev (testing)           prod (production)
    ═══════════════          ═══════════════         ═══════════════

    Write code               Receive features        Stable releases
    Commit freely             Test thoroughly          Verified only
    All files welcome         Working code only        Battle-tested
         │                         │                        │
         │    /cherry-pick         │    /merge-to-prod      │
         ├────────────────────────▶├───────────────────────▶│
         │                         │                        │
         │                    /deploy-dev              /deploy-prod
         │                         │                        │
         │                    DEV server               PROD server
         │                         │                        │
         │◄────────────────────────┘                        │
         │    always return to local                        │
         │◄────────────────────────────────────────────────┘
              always return to local


    ┌──────────────────────────────────────────────────────────────┐
    │  CRITICAL: After ANY operation — ALWAYS return to `local`!   │
    │  main branch is FROZEN (archive only)                        │
    └──────────────────────────────────────────────────────────────┘
```

---

## 6. Deploy Pipeline — Full Lifecycle

```
    Developer                      Claude Code                     Infrastructure
    ─────────                      ──────────                      ──────────────

    "deploy to dev"
         │
         ▼
    ┌─────────────────────────────────────────────────────────┐
    │                    /deploy-dev                           │
    │                                                         │
    │  1. Check branch = dev          ──▶ warn if wrong       │
    │  2. Check remote sync           ──▶ warn if behind      │
    │  3. Run deploy command          ──────────────────────▶ DEV Server
    │  4. Check logs                  ◀──────────────────────  logs
    │  5. Update _status/DEV.md                               │
    │  6. Return to local branch                              │
    └─────────────────────────────────────────────────────────┘
         │
         ▼
    Test on DEV
         │
    "deploy to prod"
         │
         ▼
    ┌─────────────────────────────────────────────────────────┐
    │                    /deploy-prod                          │
    │                                                         │
    │  1. SAFETY CHECKLIST (4 items)  ──▶ ALL must pass       │
    │     [ ] Tested on DEV?                                  │
    │     [ ] All tests pass?                                 │
    │     [ ] No critical bugs?                               │
    │     [ ] Ready for PROD?                                 │
    │  2. Explicit user confirmation  ──▶ REQUIRED            │
    │  3. Check branch = prod                                 │
    │  4. Run deploy command          ──────────────────────▶ PROD Server
    │  5. Check logs                  ◀──────────────────────  logs
    │  6. POST-DEPLOY (5 steps):                              │
    │     a) Test PROD works                                  │
    │     b) Run /docs                                        │
    │     c) Update VERSION (semver)                           │
    │     d) Update _changelogs/prod.md                       │
    │     e) Sync branches                                    │
    │  7. Return to local branch                              │
    └─────────────────────────────────────────────────────────┘
```

---

## 7. Documentation Ecosystem

```
┌─────────────────────────────────────────────────────────────────┐
│                   DOCUMENTATION FLOW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────┐                                │
│  │    /docs skill triggers     │                                │
│  │    after every deploy       │                                │
│  └─────────────┬───────────────┘                                │
│                │                                                │
│                ▼                                                │
│  ┌─────────────────────────────────────────────────────┐        │
│  │                _status/                              │        │
│  │                                                     │        │
│  │  DEV.md ──────── What's deployed on DEV             │        │
│  │  PROD.md ─────── What's deployed on PROD            │        │
│  │  PENDING_RELEASE.md ── Diff: DEV vs PROD            │        │
│  │  DEVELOPMENT_STATUS.md ── "Where I left off"        │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐        │
│  │                documentation/                        │        │
│  │                                                     │        │
│  │  ARCHITECTURE.md ──── System design & layers         │        │
│  │  ERROR_REGISTRY.md ── Root causes & fixes (newest 1st)│       │
│  │  SYSTEM_ARCHITECTURE.md ── This file (visual maps)   │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐        │
│  │                _changelogs/                          │        │
│  │                                                     │        │
│  │  dev.md ──────── DEV release history                 │        │
│  │  prod.md ─────── PROD release history                │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐        │
│  │                _specs/                               │        │
│  │                                                     │        │
│  │  README.md ───── Spec index                          │        │
│  │  brief.md → plan.md → prd.md (priority order)        │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐        │
│  │                backlog/                              │        │
│  │                                                     │        │
│  │  README.md ───── Task SSoT (ID, priority, status)    │        │
│  │  Managed via /project-manager                        │        │
│  └─────────────────────────────────────────────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Error Learning Cycle

```
    ┌─────────────────────────────────────────────────────────┐
    │              ERROR LEARNING SYSTEM                       │
    │              (auto-triggered rule)                       │
    └─────────────────────────────────────────────────────────┘

    Trigger Events:
    ● Bugfix completed
    ● Failed deploy
    ● 2+ failed attempts at a task

         │
         ▼
    ┌─────────────────────────────────────┐
    │  1. RECORD in error-log.md          │
    │                                     │
    │  - Symptom (what user saw)          │
    │  - Root Cause (WHY, dig deep)       │
    │  - Fix (exact code change)          │
    │  - Prevention (how to avoid)        │
    │  - Files (affected)                 │
    └────────────────┬────────────────────┘
                     │
                     ▼
    ┌─────────────────────────────────────┐
    │  2. UPDATE INSTRUCTIONS             │
    │     (if error reveals a gap)        │
    │                                     │
    │  ┌───────────┐  ┌───────────────┐   │
    │  │ CLAUDE.md │  │  MEMORY.md    │   │
    │  │ (project) │  │  (cross-repo) │   │
    │  └───────────┘  └───────────────┘   │
    └────────────────┬────────────────────┘
                     │
                     ▼
    ┌─────────────────────────────────────┐
    │  3. RULE OF THREE                   │
    │                                     │
    │  1st occurrence:                    │
    │    → Record + fix if obvious        │
    │                                     │
    │  2nd occurrence:                    │
    │    → Note the pattern               │
    │                                     │
    │  3rd occurrence:                    │
    │    → CODIFY as permanent rule       │
    │    → Add to CLAUDE.md or rules/     │
    └─────────────────────────────────────┘

    Data Flow:

    error happens → error-log.md → (pattern?) → CLAUDE.md / rules/
                         │                            │
                         ▼                            ▼
                    ERROR_REGISTRY.md          Future prevention
                    (documentation/)
```

---

## 9. Information Architecture — Tagging System

```
    ┌─────────────────────────────────────────────────────────────┐
    │              INFORMATION TAGS                                │
    │              (No-Duplication Principle)                      │
    ├─────────────────────────────────────────────────────────────┤
    │                                                             │
    │  [CANONICAL]                                                │
    │  ════════════                                               │
    │  THE single authoritative source for this information.      │
    │  Only ONE canonical source per fact.                        │
    │                                                             │
    │  Example: Stack info is [CANONICAL] in CLAUDE.md            │
    │           → all other files REFERENCE it                    │
    │                                                             │
    │  [REF: path#section]                                        │
    │  ═══════════════════                                        │
    │  Points to canonical source. Never duplicate — link.        │
    │                                                             │
    │  Example: [REF: CLAUDE.md#стек]                             │
    │                                                             │
    │  [CONFIRMED: source]                                        │
    │  ════════════════════                                       │
    │  Verified information with attribution.                     │
    │                                                             │
    │  Example: [CONFIRMED: deploy 2026-02-15]                    │
    │                                                             │
    │  [PLACEHOLDER: owner]                                       │
    │  ══════════════════════                                     │
    │  Information pending — someone needs to fill this in.       │
    │                                                             │
    │  Example: [PLACEHOLDER: backend-dev]                        │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘

    Flow: Write once → Reference everywhere → Never duplicate
```

---

## 10. Settings & Hooks

```
    ┌─────────────────────────────────────────────────────────────┐
    │            .claude/settings.json                            │
    ├─────────────────────────────────────────────────────────────┤
    │                                                             │
    │  PERMISSIONS                                                │
    │  ───────────                                                │
    │  allow:                                                     │
    │    WebFetch(domain:docs.anthropic.com)                      │
    │                                                             │
    │  HOOKS                                                      │
    │  ─────                                                      │
    │  PostToolUse → Write → *.py                                 │
    │                                                             │
    │    ┌───────┐     ┌───────┐     ┌─────────────────┐          │
    │    │ Claude│────▶│ Write │────▶│ Is it .py file? │          │
    │    │ edits │     │ tool  │     └────────┬────────┘          │
    │    │ file  │     └───────┘              │                   │
    │    └───────┘                    yes ◄───┘───▶ no            │
    │                                 │              │            │
    │                                 ▼              ▼            │
    │                          ruff check        (nothing)        │
    │                          --fix                              │
    │                          (auto-format)                      │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
```

---

## 11. Typical Development Session Flow

```
    ┌──────────────────────────────────────────────────────────────────┐
    │                  A DAY IN THE LIFE                               │
    └──────────────────────────────────────────────────────────────────┘

    START SESSION
         │
         ├──▶ Claude reads: CLAUDE.md + .claude/rules/ + .claude/settings.json
         │
         ▼
    /architect ──────────▶ Plan the feature
         │
         ▼
    Write code ──────────▶ (ruff auto-fix on .py via hook)
         │
         ▼
    /test ───────────────▶ lint → types → unit → build
         │
         ├── FAIL? ──────▶ Fix → /test again
         │                      │
         │                      ▼ (error-learning rule triggers)
         │                      Record in error-log.md
         │
         ├── PASS ✓
         │
         ▼
    /commit ─────────────▶ AI generates commit message
         │
         ▼
    /cherry-pick ────────▶ local → dev
         │
         ▼
    /deploy-dev ─────────▶ Deploy + check logs
         │
         ├── Test on DEV server
         │
         ├── BUG? ──────▶ Return to local → fix → repeat
         │
         ├── OK ✓
         │
         ▼
    /merge-to-prod ──────▶ dev → prod (with confirmation)
         │
         ▼
    /deploy-prod ────────▶ Safety checklist → deploy → check logs
         │
         ▼
    /docs ───────────────▶ Update _status/ + changelogs
         │
         ▼
    /git-status ─────────▶ Verify all branches synced
         │
         ▼
    auto-backup rule ────▶ "Backup to GitHub? Say yes."
         │
         ▼
    END SESSION
         │
         └──▶ DEVELOPMENT_STATUS.md = "Where I left off"
```

---

## 12. Complete File Tree with Purpose

```
WORKSPACE/
│
├── CLAUDE.md                          ★ Master instructions for Claude
├── VERSION                            ★ Semantic version (0.0.1)
├── .gitignore                         ★ Security: no .env, no secrets
│
├── .claude/                           ── AI BRAIN ──
│   ├── settings.json                  Permissions + hooks
│   ├── settings.local.json            Personal overrides (gitignored)
│   │
│   ├── rules/                         Auto-triggered behaviors
│   │   ├── error-learning.md          Record & learn from failures
│   │   └── auto-backup.md            Suggest backup after changes
│   │
│   ├── agents/                        Delegated specialists
│   │   ├── deployer.md                Deploy with safety checks
│   │   ├── docs-generator.md          Update status files
│   │   └── test-runner.md             Run all test types
│   │
│   ├── skills/                        /slash commands (12 total)
│   │   ├── README.md                  Skill catalog
│   │   ├── commit/SKILL.md            AI commit messages
│   │   ├── push/SKILL.md              Safe push
│   │   ├── cherry-pick/SKILL.md       local → dev
│   │   ├── merge-to-prod/SKILL.md     dev → prod
│   │   ├── git-status/SKILL.md        Branch overview
│   │   ├── deploy-dev/SKILL.md        Deploy DEV
│   │   ├── deploy-prod/SKILL.md       Deploy PROD
│   │   ├── test/SKILL.md              Testing pipeline
│   │   ├── docs/SKILL.md              Post-deploy docs
│   │   ├── techdebt/SKILL.md          Tech debt scan
│   │   ├── architect/SKILL.md         Architecture planning
│   │   └── project-manager/           PM skill
│   │       ├── SKILL.md               Backlog management
│   │       └── references/
│   │           └── role.md            PM role definition
│   │
│   └── data/                          Persistent AI data
│       └── error-log.md               Error history
│
├── _status/                           ── ENVIRONMENTS ──
│   ├── DEV.md                         DEV state
│   ├── PROD.md                        PROD state
│   ├── PENDING_RELEASE.md             DEV→PROD diff
│   └── DEVELOPMENT_STATUS.md          Current work state
│
├── _changelogs/                       ── RELEASE HISTORY ──
│   ├── dev.md                         DEV releases
│   └── prod.md                        PROD releases
│
├── _specs/                            ── SPECIFICATIONS ──
│   └── README.md                      Spec index + priority rules
│
├── backlog/                           ── TASK MANAGEMENT ──
│   └── README.md                      Task SSoT + format rules
│
├── documentation/                     ── DOCUMENTATION ──
│   ├── README.md                      Doc index
│   ├── ARCHITECTURE.md                System design template
│   ├── ERROR_REGISTRY.md              Public error registry
│   └── SYSTEM_ARCHITECTURE.md         ★ THIS FILE (visual maps)
│
└── _specs/
    ├── README.md                      Spec index + priority rules
    └── RECOMMENDED_SYSTEM.md          Blueprint for this system
```

---

## 13. Data Relationships

```
                    ┌────────────┐
                    │  CLAUDE.md │
                    │  (master)  │
                    └─────┬──────┘
                          │ references
          ┌───────────────┼───────────────────┐
          │               │                   │
          ▼               ▼                   ▼
    ┌───────────┐   ┌──────────┐       ┌───────────┐
    │ .claude/  │   │ _status/ │       │ backlog/  │
    │ skills/   │   │          │       │           │
    │ agents/   │   │ DEV.md ◄─┼─ /docs│ README.md │◄── /project-manager
    │ rules/    │   │ PROD.md  │       │           │
    └─────┬─────┘   └────┬─────┘       └───────────┘
          │              │
          │              │ feeds
          ▼              ▼
    ┌───────────┐   ┌──────────────┐
    │ .claude/  │   │ _changelogs/ │
    │ data/     │   │              │
    │           │   │ dev.md       │
    │ error-log │   │ prod.md      │
    └─────┬─────┘   └──────────────┘
          │
          │ feeds
          ▼
    ┌──────────────────┐
    │ documentation/   │
    │                  │
    │ ERROR_REGISTRY   │◄── error-learning rule
    │ ARCHITECTURE     │◄── /architect
    └──────────────────┘

    ┌──────────────────┐
    │ _specs/          │
    │                  │
    │ brief → plan     │◄── /architect + /project-manager
    │    → prd         │
    └──────────────────┘
```

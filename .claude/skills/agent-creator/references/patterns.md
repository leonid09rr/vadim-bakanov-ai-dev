# Agent Patterns

Anthropic's 6 composable patterns for building agentic systems. Start simple — add complexity only when needed.

## Table of Contents

1. [Decision Guide](#decision-guide)
2. [Prompt Chaining](#1-prompt-chaining)
3. [Routing](#2-routing)
4. [Parallelization](#3-parallelization)
5. [Orchestrator-Workers](#4-orchestrator-workers)
6. [Evaluator-Optimizer](#5-evaluator-optimizer)
7. [Autonomous Agent](#6-autonomous-agent)

## Decision Guide

```
Is the task a single step?
├── YES → Single query() call
└── NO → Are subtasks known in advance?
    ├── YES → Are they independent?
    │   ├── YES → Pattern 3: Parallelization
    │   └── NO → Pattern 1: Prompt Chaining
    └── NO → Does the task need classification first?
        ├── YES → Pattern 2: Routing
        └── NO → Are subtasks determined dynamically?
            ├── YES → Pattern 4: Orchestrator-Workers
            └── NO → Does output need iterative refinement?
                ├── YES → Pattern 5: Evaluator-Optimizer
                └── NO → Pattern 6: Autonomous Agent
```

## 1. Prompt Chaining

Sequential LLM calls where each processes the previous output. Add programmatic "gates" between steps.

```
[Input] → LLM₁ → Gate → LLM₂ → Gate → LLM₃ → [Output]
```

**When:** Task decomposes into fixed subtasks; accuracy > latency.

**Implementation:**

```python
# Step 1: Generate outline
outline = await single_query("Create outline for: " + topic)

# Gate: validate outline has 3+ sections
if outline.count("##") < 3:
    outline = await single_query("Expand this outline to 3+ sections: " + outline)

# Step 2: Write content from outline
content = await single_query("Write article from outline: " + outline)
```

**Examples:**
- Generate marketing copy → Translate to other languages
- Create outline (validate) → Write full document
- Parse data → Transform → Validate → Store

---

## 2. Routing

Classify input, then route to specialized handlers.

```
[Input] → Classifier → ┬→ Handler A
                        ├→ Handler B
                        └→ Handler C
```

**When:** Distinct input categories needing different processing.

**Implementation:**

```python
# Router agent classifies and delegates
options = ClaudeAgentOptions(
    system_prompt="Classify the request and delegate to the right specialist.",
    allowed_tools=["Task"],
    agents={
        "refund-handler": AgentDefinition(
            description="Handle refund requests",
            prompt="Process refund requests. Verify eligibility, calculate amount.",
            tools=["Read", "Bash"],
            model="haiku",
        ),
        "technical-support": AgentDefinition(
            description="Handle technical issues and bug reports",
            prompt="Diagnose technical issues. Check logs, suggest fixes.",
            tools=["Read", "Grep", "Bash"],
            model="sonnet",
        ),
        "general-inquiry": AgentDefinition(
            description="Handle general questions about products and services",
            prompt="Answer general questions using knowledge base.",
            tools=["Read", "WebSearch"],
            model="haiku",
        ),
    },
)
```

**Examples:**
- Customer support: route by issue type
- Code review: route by language/framework
- Query complexity: simple → Haiku, complex → Opus

---

## 3. Parallelization

Multiple LLM calls simultaneously, results aggregated.

```
         ┌→ LLM₁ →┐
[Input] →├→ LLM₂ →├→ [Aggregate]
         └→ LLM₃ →┘
```

Two variations:
- **Sectioning:** Independent subtasks in parallel
- **Voting:** Same task N times, majority wins

**When:** Subtasks are independent; multiple perspectives increase confidence.

**Implementation (Sectioning):**

```python
options = ClaudeAgentOptions(
    system_prompt="""Review this codebase for issues.
Launch ALL THREE reviewers in parallel (single message, multiple Task calls).""",
    allowed_tools=["Read", "Task"],
    agents={
        "security-reviewer": AgentDefinition(
            description="Check for security vulnerabilities",
            prompt="Focus ONLY on security: injection, XSS, auth, secrets.",
            tools=["Read", "Grep", "Glob"],
        ),
        "logic-reviewer": AgentDefinition(
            description="Check for logic errors and race conditions",
            prompt="Focus ONLY on logic: null handling, off-by-one, races.",
            tools=["Read", "Grep", "Glob"],
        ),
        "quality-reviewer": AgentDefinition(
            description="Check for code quality and DRY violations",
            prompt="Focus ONLY on quality: naming, duplication, patterns.",
            tools=["Read", "Grep", "Glob"],
        ),
    },
)
```

**Implementation (Voting):**

```python
# 3 independent agents classify the same input
# Aggregate: majority vote
agents = {
    f"classifier-{i}": AgentDefinition(
        description=f"Classify text intent (instance {i})",
        prompt="Classify as: positive, negative, neutral. Output JSON.",
        tools=[],
        model="haiku",
    )
    for i in range(3)
}
```

**Examples:**
- Security + Logic + Quality reviews in parallel
- Guardrails running alongside main query
- Multiple classifiers for high-confidence labeling

---

## 4. Orchestrator-Workers

Central agent dynamically breaks down tasks and delegates.

```
[Input] → Orchestrator → ┬→ Worker₁ →┐
                          ├→ Worker₂ →├→ Orchestrator → [Output]
                          └→ Worker₃ →┘
```

**Key difference from Parallelization:** Subtasks are NOT predefined — the orchestrator determines them based on input.

**When:** Complex tasks where breakdown depends on context.

**Implementation:**

```python
options = ClaudeAgentOptions(
    system_prompt="""You are a project manager. Analyze the task, break it into
subtasks, assign each to the appropriate specialist, then synthesize results.""",
    allowed_tools=["Read", "Grep", "Glob", "Task"],
    model="opus",  # Smart orchestrator
    agents={
        "frontend-dev": AgentDefinition(
            description="Implement frontend changes (React, CSS, HTML)",
            prompt="You are a frontend developer. Implement the requested UI changes.",
            tools=["Read", "Write", "Edit", "Glob", "Grep", "Bash"],
            model="sonnet",
        ),
        "backend-dev": AgentDefinition(
            description="Implement backend changes (API, database, services)",
            prompt="You are a backend developer. Implement the requested API/service changes.",
            tools=["Read", "Write", "Edit", "Glob", "Grep", "Bash"],
            model="sonnet",
        ),
        "test-writer": AgentDefinition(
            description="Write and run tests for new functionality",
            prompt="You are a test engineer. Write comprehensive tests.",
            tools=["Read", "Write", "Edit", "Bash", "Grep"],
            model="sonnet",
        ),
    },
)
```

**Examples:**
- Multi-file code changes (orchestrator decides which files)
- Research tasks (orchestrator decides which sources)
- Data pipeline (orchestrator decides transformation steps)

---

## 5. Evaluator-Optimizer

One agent generates, another evaluates, iterating until quality threshold met.

```
[Input] → Generator → Evaluator → ┬→ [Accept] → Output
                ↑                  │
                └──── Feedback ────┘
```

**When:** Clear evaluation criteria exist; iterative refinement helps.

**Implementation:**

```python
options = ClaudeAgentOptions(
    system_prompt="""Generate code, then use the evaluator to check quality.
If score < 8/10, incorporate feedback and regenerate. Max 3 iterations.""",
    allowed_tools=["Read", "Write", "Edit", "Task"],
    agents={
        "evaluator": AgentDefinition(
            description="Evaluate code quality on a 1-10 scale with feedback",
            prompt="""Score the code 1-10 on: correctness, performance, readability.
Output JSON: {"score": N, "feedback": "...", "issues": [...]}""",
            tools=["Read", "Grep"],
            model="opus",  # Best model for evaluation
        ),
    },
)
```

**Examples:**
- Code generation with quality checks
- Content writing with editorial review
- Translation with accuracy verification

---

## 6. Autonomous Agent

Agent operates in a loop with tools, making dynamic decisions.

```
[Input] → Agent ←→ Tools ←→ Environment
              ↓
         [Checkpoint] → Human review
              ↓
         [Continue/Stop]
```

**When:** Open-ended problems; step count unpredictable.

**Implementation:**

```python
options = ClaudeAgentOptions(
    system_prompt="""You are an autonomous debugging agent.
1. Reproduce the bug
2. Find root cause
3. Implement fix
4. Verify fix passes tests
Ask user for confirmation before committing.""",
    allowed_tools=["Read", "Write", "Edit", "Bash", "Grep", "Glob", "AskUserQuestion"],
    max_turns=50,
    max_budget_usd=5.0,  # Safety budget limit
)
```

**Key safeguards:**
- `max_turns` — prevent infinite loops
- `max_budget_usd` — cost ceiling
- `AskUserQuestion` — human-in-the-loop checkpoints
- Hooks — block dangerous operations

**Examples:**
- Bug fixing (unknown steps to resolution)
- Environment setup (depends on what's installed)
- Data exploration (depends on what's found)

---

## Combining Patterns

Patterns compose naturally:

```
Routing → Parallelization → Evaluator-Optimizer
  │              │                    │
  │    ┌─── Workers ───┐        ┌── Check ──┐
Input → Classify → ├→ Specialist A →├→ Evaluate →├→ Accept
                   ├→ Specialist B →│           └→ Retry
                   └→ Specialist C →┘
```

**Real-world example (Anthropic's Research System):**
- **Orchestrator** (Opus): Decomposes query, manages subagents
- **Workers** (Sonnet): Execute specialized searches in parallel
- **Evaluator**: Verifies source quality and citation accuracy
- Result: 90.2% better than single-agent Opus

## Key Insight

> "Start with the simplest solution possible. Many applications benefit from optimizing single LLM calls with retrieval and in-context examples rather than building agentic systems." — Anthropic

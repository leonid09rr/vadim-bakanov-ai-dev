# Advanced Examples

## Table of Contents

1. [Interactive Sessions (ClaudeSDKClient)](#interactive-sessions)
2. [Structured Output](#structured-output)
3. [Session Management](#session-management)
4. [Agent Teams](#agent-teams)
5. [Production Patterns](#production-patterns)
6. [Dynamic Agent Configuration](#dynamic-agent-configuration)

## Interactive Sessions

`ClaudeSDKClient` maintains conversation state across multiple exchanges.

### Python

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

async with ClaudeSDKClient(options=ClaudeAgentOptions(
    allowed_tools=["Read", "Write", "Edit", "Bash", "Grep", "Glob"],
)) as client:
    # First query
    await client.query("Read the authentication module in src/auth/")
    async for msg in client.receive_response():
        print(msg)

    # Follow-up — Claude remembers the context
    await client.query("Find all places that import from this module")
    async for msg in client.receive_response():
        print(msg)

    # Another follow-up
    await client.query("Refactor the login function to use async/await")
    async for msg in client.receive_response():
        print(msg)
```

### TypeScript

```typescript
import { ClaudeSDKClient, ClaudeAgentOptions } from "@anthropic-ai/claude-agent-sdk";

const client = new ClaudeSDKClient({
  allowedTools: ["Read", "Write", "Edit", "Bash"],
});

await client.connect("Read the auth module");
for await (const msg of client.receiveResponse()) {
  console.log(msg);
}

// Follow-up with full context
await client.query("Now add rate limiting to the login endpoint");
for await (const msg of client.receiveResponse()) {
  console.log(msg);
}

// Interrupt mid-execution if needed
await client.interrupt();

await client.disconnect();
```

### Key Methods

| Method | Description |
|--------|-------------|
| `connect(prompt)` | Start session with optional initial prompt |
| `query(prompt, session_id)` | Send a new request |
| `receive_messages()` | Async iterator for all messages |
| `receive_response()` | Async iterator until response complete |
| `interrupt()` | Stop mid-execution |
| `rewind_files(uuid)` | Restore files to a previous state |
| `disconnect()` | Close connection |

**Note:** `rewind_files` requires `enable_file_checkpointing=True` in options.

---

## Structured Output

Force agent to return data in a specific JSON schema.

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Grep", "Glob"],
    output_format={
        "type": "json_schema",
        "schema": {
            "type": "object",
            "properties": {
                "issues": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "severity": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
                            "file": {"type": "string"},
                            "line": {"type": "integer"},
                            "description": {"type": "string"},
                            "fix": {"type": "string"},
                        },
                        "required": ["severity", "file", "description"],
                    },
                },
                "summary": {"type": "string"},
                "score": {"type": "number", "minimum": 0, "maximum": 10},
            },
            "required": ["issues", "summary", "score"],
        },
    },
)
```

---

## Session Management

### Resuming Sessions

```python
# First query — capture session_id
session_id = None
async for msg in query(prompt="Analyze the codebase", options=options):
    if hasattr(msg, "subtype") and msg.subtype == "init":
        session_id = msg.session_id
    print(msg)

# Later — resume with full context preserved
async for msg in query(
    prompt="Now implement the changes we discussed",
    options=ClaudeAgentOptions(resume=session_id),
):
    print(msg)
```

### Forking Sessions

```python
# Fork creates a new session with the same context but divergent history
options = ClaudeAgentOptions(
    fork_session=original_session_id,
)
```

---

## Agent Teams

Agent teams are independent Claude instances that coordinate via shared task lists and messaging. Experimental feature.

### Enable

```json
// settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### Architecture

```
┌─────────────────────────────────────────┐
│              Team Lead                   │
│  (Creates team, spawns, coordinates)     │
├─────────┬──────────┬──────────┬─────────┤
│Teammate1│Teammate2 │Teammate3 │   ...   │
│(own ctx)│(own ctx) │(own ctx) │         │
├─────────┴──────────┴──────────┴─────────┤
│          Shared Task List               │
│     (dependency tracking, claiming)      │
├─────────────────────────────────────────┤
│          Mailbox System                  │
│     (inter-agent messaging)             │
└─────────────────────────────────────────┘
```

### Subagents vs Agent Teams

| Aspect | Subagents | Agent Teams |
|--------|----------|-------------|
| Context | Own context; results return to caller | Fully independent contexts |
| Communication | Report back to main agent only | Direct inter-agent messaging |
| Coordination | Main agent manages everything | Shared task list, self-coordination |
| Best for | Focused tasks needing only the result | Complex work needing discussion |
| Token cost | Lower (results summarized) | Higher (each is separate instance) |
| Nesting | Cannot spawn sub-subagents | Cannot create sub-teams |

### When to Use Agent Teams

- Research with multiple perspectives
- New features with cross-layer changes (frontend + backend + tests)
- Debugging with competing hypotheses
- Large refactoring across many files

### Quality Gates (Hooks)

```python
# TeammateIdle: Runs when teammate is about to go idle
# Exit code 2 → send feedback, keep working

# TaskCompleted: Runs when task is being marked complete
# Exit code 2 → prevent completion, send feedback
```

### Limitations

- No session resumption with in-process teammates
- One team per session
- No nested teams
- Lead is fixed for the team's lifetime
- Significantly higher token usage

---

## Production Patterns

Lessons from Anthropic's multi-agent research system.

### 1. External Memory

Agents save plans to external storage before context limits approach.

```python
@tool("save_plan", "Save research plan to external storage", {"plan": str})
async def save_plan(args):
    await storage.save("plan.md", args["plan"])
    return {"content": [{"type": "text", "text": "Plan saved."}]}

# Agent prompt includes:
# "Before context gets large, save your plan using save_plan tool."
```

### 2. Artifact-Based Communication

Subagents store results in files, pass lightweight references.

```python
# Worker agent saves results to file
worker_prompt = """
Save your findings to: /tmp/results/{task_id}.json
Output only the file path when done.
"""

# Orchestrator reads results from files
orchestrator_prompt = """
Each worker saves results as JSON files. Read and synthesize them.
"""
```

### 3. Budget and Safety Controls

```python
options = ClaudeAgentOptions(
    max_turns=50,              # Prevent infinite loops
    max_budget_usd=10.0,       # Cost ceiling
    permission_mode="acceptEdits",  # Auto-accept file edits
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[block_dangerous_commands]),
        ],
    },
)
```

### 4. Model Selection Strategy

```python
# Opus for orchestration and critical decisions
orchestrator_model = "opus"

# Sonnet for standard implementation work
worker_model = "sonnet"

# Haiku for simple, high-volume tasks
classifier_model = "haiku"

# Key insight from Anthropic:
# Upgrading model quality gives LARGER gains than doubling token budget
```

### 5. Parallel Tool Calling

Instruct agents to make multiple tool calls simultaneously:

```python
system_prompt = """When you need to search multiple files or run multiple analyses,
make ALL independent tool calls in a single message. This cuts execution time
significantly.

Example: If you need to read 3 files, call Read 3 times in one message,
not 3 separate messages."""
```

### 6. End-State Evaluation

Validate final outputs, not every intermediate step:

```python
# BAD: Check after every tool call
# GOOD: Validate the final result

evaluator = AgentDefinition(
    description="Evaluate the final output quality",
    prompt="""Evaluate ONLY the final deliverable:
1. Does it meet all requirements?
2. Is it correct and complete?
3. Score 1-10 with justification.
Do NOT evaluate intermediate steps.""",
    tools=["Read"],
    model="opus",
)
```

### 7. Setting Sources for Project Context

By default, the SDK loads NO filesystem settings. To access CLAUDE.md and project settings:

```python
options = ClaudeAgentOptions(
    system_prompt={"type": "preset", "preset": "claude_code"},
    setting_sources=["project"],  # Required to load CLAUDE.md
)
```

| Source | What It Loads |
|--------|--------------|
| `"user"` | User-level settings |
| `"project"` | CLAUDE.md, project rules |
| `"local"` | Local environment settings |

---

## Dynamic Agent Configuration

### Factory Pattern

```python
def create_reviewer(language: str, strictness: str) -> AgentDefinition:
    strict = strictness == "strict"
    return AgentDefinition(
        description=f"Review {language} code for issues",
        prompt=f"""You are a {'strict' if strict else 'balanced'} {language} code reviewer.
{'Flag ALL potential issues, even minor ones.' if strict else 'Focus on significant issues only.'}""",
        tools=["Read", "Grep", "Glob"],
        model="opus" if strict else "sonnet",
    )

# Usage
agents = {
    "py-reviewer": create_reviewer("Python", "strict"),
    "js-reviewer": create_reviewer("JavaScript", "balanced"),
    "go-reviewer": create_reviewer("Go", "strict"),
}
```

### Conditional Agents

```python
def build_agents(task_type: str) -> dict:
    agents = {}

    if task_type in ("feature", "refactor"):
        agents["coder"] = AgentDefinition(
            description="Implement code changes",
            prompt="You are a developer...",
            tools=["Read", "Write", "Edit", "Bash", "Grep", "Glob"],
        )

    if task_type in ("feature", "bugfix"):
        agents["tester"] = AgentDefinition(
            description="Write and run tests",
            prompt="You are a test engineer...",
            tools=["Read", "Write", "Bash", "Grep"],
        )

    # Always include reviewer
    agents["reviewer"] = AgentDefinition(
        description="Review code changes",
        prompt="You are a code reviewer...",
        tools=["Read", "Grep", "Glob"],
    )

    return agents
```

### Permission Handler

```python
async def custom_permissions(tool_name, input_data, context):
    # Auto-allow read operations
    if tool_name in ("Read", "Grep", "Glob"):
        return PermissionResultAllow(updated_input=input_data)

    # Block writes to protected paths
    path = input_data.get("file_path", "")
    protected = [".env", "secrets", "credentials"]
    if any(p in path for p in protected):
        return PermissionResultDeny(
            message=f"Protected path: {path}",
            interrupt=True,
        )

    # Ask for everything else
    return PermissionResultAsk()

options = ClaudeAgentOptions(can_use_tool=custom_permissions)
```

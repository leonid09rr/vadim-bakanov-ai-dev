---
name: agent-creator
description: Design and build multi-agent systems using the Anthropic Claude Agent SDK (Python/TypeScript). Use when the user wants to: (1) create an agent or sub-agent (subagent), (2) build a multi-agent system or agent team, (3) design agentic workflows with tools, hooks, or MCP servers, (4) implement agent patterns (orchestrator-workers, prompt chaining, routing, parallelization, evaluator-optimizer), (5) understand how Claude Agent SDK works (query, ClaudeSDKClient, AgentDefinition, HookMatcher). Triggers on: "создай агента", "сделай суб-агента", "build an agent", "create a subagent", "multi-agent", "agent SDK", "агентная архитектура".
---

# Agent Creator

Build production-grade multi-agent systems with the Claude Agent SDK.

## Quick Reference

| Component | Purpose |
|-----------|---------|
| `query()` | One-shot async tasks (no state) |
| `ClaudeSDKClient` | Interactive sessions (state, interrupts, hooks) |
| `AgentDefinition` | Subagent definition (name, prompt, tools, model) |
| `HookMatcher` | Intercept tool calls (validate, block, modify) |
| `create_sdk_mcp_server` | Custom tools via MCP |

## Workflow

### Step 1: Understand the Use Case

Ask the user:
1. What problem does the agent system solve?
2. Single agent or multi-agent? If multi — what are the roles?
3. Python or TypeScript?
4. What tools does each agent need? (file I/O, web search, bash, custom)
5. What's the coordination pattern? (see references/patterns.md)

### Step 2: Choose Architecture

Based on complexity:

| Complexity | Architecture | When |
|------------|-------------|------|
| Simple | Single `query()` call | One-shot task, no follow-ups |
| Medium | `ClaudeSDKClient` + subagents | Multiple roles, need context |
| Complex | Agent Teams | Independent workers, inter-agent messaging |

For pattern selection details, see [references/patterns.md](references/patterns.md).

### Step 3: Design Agent Definitions

For each agent, define:

```python
AgentDefinition(
    description="When to use this agent (Claude reads this to decide)",
    prompt="Role, behavior, output format",
    tools=["Read", "Grep", "Glob"],  # Minimal needed tools
    model="sonnet",  # Cost-efficient default
)
```

**Rules:**
- `description` — triggers invocation; make it clear and specific
- `tools` — principle of least privilege; read-only for analysis agents
- **Never** include `Task` in subagent tools (subagents cannot spawn subagents)
- Use `model` overrides: `"opus"` for lead/critical decisions, `"sonnet"` for workers, `"haiku"` for simple tasks

Common tool sets: see [references/tools-and-hooks.md](references/tools-and-hooks.md).

### Step 4: Implement

#### Minimal Example (Python)

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for msg in query(
        prompt="Analyze auth.py for security issues",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Grep", "Glob"],
        ),
    ):
        print(msg)

asyncio.run(main())
```

#### Multi-Agent Example (Python)

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition

options = ClaudeAgentOptions(
    system_prompt="You are a code review orchestrator.",
    allowed_tools=["Read", "Grep", "Glob", "Task"],  # Task required for subagents
    agents={
        "security-reviewer": AgentDefinition(
            description="Review code for security vulnerabilities (injection, XSS, auth bypasses)",
            prompt="You are a security expert. Report: severity, location, fix.",
            tools=["Read", "Grep", "Glob"],
            model="sonnet",
        ),
        "logic-reviewer": AgentDefinition(
            description="Review code for logic errors, race conditions, edge cases",
            prompt="You are a logic analysis expert. Report: issue, impact, fix.",
            tools=["Read", "Grep", "Glob"],
            model="sonnet",
        ),
    },
)

async for msg in query(prompt="Review src/api/ for issues", options=options):
    print(msg)
```

#### TypeScript Example

```typescript
import { query, ClaudeAgentOptions, AgentDefinition } from "@anthropic-ai/claude-agent-sdk";

const options: ClaudeAgentOptions = {
  allowedTools: ["Read", "Grep", "Glob", "Task"],
  agents: {
    "test-runner": {
      description: "Run tests and analyze failures",
      prompt: "You are a test execution specialist...",
      tools: ["Bash", "Read", "Grep"],
      model: "sonnet",
    },
  },
};

for await (const msg of query("Run all tests and report failures", options)) {
  console.log(msg);
}
```

For interactive sessions, hooks, custom tools, and advanced patterns, see [references/advanced-examples.md](references/advanced-examples.md).

### Step 5: Add Hooks (Optional)

Hooks intercept execution at key points:

```python
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

async def block_env_writes(input_data, tool_use_id, context):
    path = input_data["tool_input"].get("file_path", "")
    if path.endswith(".env"):
        return {"hookSpecificOutput": {
            "hookEventName": input_data["hook_event_name"],
            "permissionDecision": "deny",
            "permissionDecisionReason": "Cannot modify .env files",
        }}
    return {}

options = ClaudeAgentOptions(
    hooks={"PreToolUse": [HookMatcher(matcher="Write|Edit", hooks=[block_env_writes])]}
)
```

Hook events and patterns: see [references/tools-and-hooks.md](references/tools-and-hooks.md).

### Step 6: Add Custom Tools (Optional)

Custom tools via in-process MCP servers:

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("search_db", "Search the database", {"query": str, "limit": int})
async def search_db(args):
    results = await db.search(args["query"], limit=args["limit"])
    return {"content": [{"type": "text", "text": json.dumps(results)}]}

server = create_sdk_mcp_server(name="db-tools", version="1.0.0", tools=[search_db])

options = ClaudeAgentOptions(
    mcp_servers={"db": server},
    allowed_tools=["mcp__db__search_db"],  # Format: mcp__<server>__<tool>
)
```

### Step 7: Test and Iterate

1. Run with a representative task
2. Check: Are subagents invoked correctly? Are tools scoped properly?
3. Monitor token usage — multi-agent systems use significantly more tokens
4. Refine prompts based on observed behavior

## Configuration Reference

Key `ClaudeAgentOptions` fields:

| Field | Type | Description |
|-------|------|-------------|
| `system_prompt` | `str` or `{"type": "preset", "preset": "claude_code"}` | Custom or built-in prompt |
| `allowed_tools` | `list[str]` | Tools this agent can use |
| `agents` | `dict[str, AgentDefinition]` | Subagent definitions |
| `hooks` | `dict[str, list[HookMatcher]]` | Hook configurations |
| `mcp_servers` | `dict` | MCP server configs (in-process or subprocess) |
| `permission_mode` | `str` | `"default"`, `"acceptEdits"`, `"plan"`, `"bypassPermissions"` |
| `max_turns` | `int` | Max conversation turns |
| `max_budget_usd` | `float` | Budget limit |
| `model` | `str` | Model override |
| `output_format` | `dict` | JSON schema for structured output |
| `cwd` | `str` | Working directory |
| `setting_sources` | `list[str]` | `["user", "project", "local"]` — load CLAUDE.md etc. |

## Anti-Patterns

| Anti-Pattern | Why It's Bad | Fix |
|-------------|-------------|-----|
| Too many subagents | Coordination overhead > benefit | Start with 2-3, add if needed |
| Subagent with Task tool | Subagents can't spawn subagents | Remove Task from subagent tools |
| All agents use Opus | Expensive, often unnecessary | Use Sonnet for workers, Opus for lead only |
| No tool restrictions | Security risk, wasted tokens | Principle of least privilege |
| Giant system prompts | Wastes context | Keep focused, use references |
| Skipping hooks for safety | Security vulnerabilities | Add PreToolUse hooks for sensitive ops |

## References

- **[references/patterns.md](references/patterns.md)** — 6 composable agent patterns with decision guide
- **[references/tools-and-hooks.md](references/tools-and-hooks.md)** — Built-in tools, hook events, custom tools via MCP
- **[references/advanced-examples.md](references/advanced-examples.md)** — Interactive sessions, structured output, agent teams, production patterns

# Tools and Hooks Reference

## Table of Contents

1. [Built-in Tools](#built-in-tools)
2. [Common Tool Combinations](#common-tool-combinations)
3. [Custom Tools (MCP)](#custom-tools-mcp)
4. [Hook Events](#hook-events)
5. [Hook Patterns](#hook-patterns)

## Built-in Tools

| Tool | Description | Read-Only |
|------|-------------|-----------|
| `Read` | Read files | Yes |
| `Write` | Create new files | No |
| `Edit` | Precise edits to existing files | No |
| `Bash` | Run terminal commands | No |
| `Glob` | Find files by pattern | Yes |
| `Grep` | Search file contents with regex | Yes |
| `WebSearch` | Search the web | Yes |
| `WebFetch` | Fetch and parse web pages | Yes |
| `AskUserQuestion` | Ask user multiple-choice questions | Yes |
| `TodoWrite` | Manage structured task lists | No |
| `NotebookEdit` | Edit Jupyter notebook cells | No |
| `Task` | Invoke subagents | — |

**Important:** `Task` must be in the main agent's `allowed_tools` for subagent invocation. Never include `Task` in a subagent's tools.

## Common Tool Combinations

| Use Case | Tools |
|----------|-------|
| Read-only analysis | `Read`, `Grep`, `Glob` |
| Code review | `Read`, `Grep`, `Glob` (no write access) |
| Test execution | `Bash`, `Read`, `Grep` |
| Code modification | `Read`, `Edit`, `Write`, `Grep`, `Glob` |
| Full development | `Read`, `Edit`, `Write`, `Bash`, `Grep`, `Glob` |
| Research | `WebSearch`, `WebFetch`, `Read` |
| Orchestrator | `Read`, `Grep`, `Glob`, `Task` |
| Interactive | All tools + `AskUserQuestion` |

## Custom Tools (MCP)

### In-Process Server (Python)

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("get_user", "Fetch user by ID", {"user_id": int})
async def get_user(args):
    user = await db.get_user(args["user_id"])
    return {"content": [{"type": "text", "text": json.dumps(user)}]}

@tool("list_orders", "List orders for a user", {
    "user_id": int,
    "status": str,  # "pending", "shipped", "delivered"
    "limit": int,
})
async def list_orders(args):
    orders = await db.list_orders(**args)
    return {"content": [{"type": "text", "text": json.dumps(orders)}]}

server = create_sdk_mcp_server(
    name="store-api",
    version="1.0.0",
    tools=[get_user, list_orders],
)

options = ClaudeAgentOptions(
    mcp_servers={"store": server},
    allowed_tools=["mcp__store__get_user", "mcp__store__list_orders"],
)
```

### In-Process Server (TypeScript)

```typescript
import { tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

const getUser = tool(
  "get_user",
  "Fetch user by ID",
  { userId: z.number().describe("The user ID") },
  async (args) => {
    const user = await db.getUser(args.userId);
    return { content: [{ type: "text", text: JSON.stringify(user) }] };
  }
);

const server = createSdkMcpServer({
  name: "store-api",
  version: "1.0.0",
  tools: [getUser],
});
```

### External MCP Server (subprocess)

```python
options = ClaudeAgentOptions(
    mcp_servers={
        "playwright": {
            "command": "npx",
            "args": ["@playwright/mcp@latest"],
        },
        "postgres": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-postgres", CONNECTION_STRING],
        },
    },
)
```

### Complex Input Schemas (JSON Schema)

```python
@tool("search", "Search with filters", {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Search query"},
        "filters": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "enum": ["blog", "docs", "api"]},
                "date_from": {"type": "string", "format": "date"},
            },
        },
        "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 10},
    },
    "required": ["query"],
})
async def search(args):
    # ...
```

### Tool Naming Convention

Format: `mcp__<server-name>__<tool-name>`

```python
# Server named "db" with tool "query"
allowed_tools=["mcp__db__query"]

# Server named "slack" with tools "send_message" and "list_channels"
allowed_tools=["mcp__slack__send_message", "mcp__slack__list_channels"]
```

## Hook Events

| Event | Phase | Can Block | Use Case |
|-------|-------|-----------|----------|
| `PreToolUse` | Before tool execution | Yes | Validate, block, modify inputs |
| `PostToolUse` | After tool execution | No | Log, audit, add context |
| `PostToolUseFailure` | Tool execution failed (TS only) | No | Error handling, retry logic |
| `UserPromptSubmit` | User sends prompt | Yes | Input validation, routing |
| `Stop` | Agent stops execution | No | Cleanup, summary generation |
| `SubagentStart` | Subagent initialized (TS only) | No | Track subagent spawning |
| `SubagentStop` | Subagent completed | No | Collect subagent results |
| `PreCompact` | Before context compaction | No | Save important context |
| `SessionStart` | Session begins (TS only) | No | Initialization |
| `SessionEnd` | Session ends (TS only) | No | Cleanup |

## Hook Patterns

### Block Dangerous Operations

```python
async def block_production_writes(input_data, tool_use_id, context):
    cmd = input_data["tool_input"].get("command", "")
    dangerous = ["rm -rf", "DROP TABLE", "DELETE FROM", "git push --force"]
    if any(d in cmd for d in dangerous):
        return {"hookSpecificOutput": {
            "hookEventName": input_data["hook_event_name"],
            "permissionDecision": "deny",
            "permissionDecisionReason": f"Blocked dangerous command: {cmd}",
        }}
    return {}

hooks = {"PreToolUse": [HookMatcher(matcher="Bash", hooks=[block_production_writes])]}
```

### Audit Logging

```python
async def audit_log(input_data, tool_use_id, context):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "tool": input_data.get("tool_name"),
        "input": input_data.get("tool_input"),
        "agent": context.get("agent_id", "main"),
    }
    await write_audit_log(log_entry)
    return {}

hooks = {"PostToolUse": [HookMatcher(hooks=[audit_log])]}
```

### Modify Tool Input

```python
async def add_default_timeout(input_data, tool_use_id, context):
    tool_input = input_data["tool_input"]
    if "timeout" not in tool_input:
        tool_input["timeout"] = 30000
    return {"hookSpecificOutput": {
        "hookEventName": input_data["hook_event_name"],
        "permissionDecision": "allow",
        "updatedInput": tool_input,
    }}

hooks = {"PreToolUse": [HookMatcher(matcher="Bash", hooks=[add_default_timeout])]}
```

### Inject Context After Tool Use

```python
async def add_guidance(input_data, tool_use_id, context):
    return {"systemMessage": "Remember: always run tests after modifying code."}

hooks = {"PostToolUse": [HookMatcher(matcher="Edit|Write", hooks=[add_guidance])]}
```

### Rate Limiting

```python
from collections import defaultdict
import time

call_counts = defaultdict(list)

async def rate_limit(input_data, tool_use_id, context):
    tool = input_data.get("tool_name", "")
    now = time.time()
    # Clean old entries (older than 60s)
    call_counts[tool] = [t for t in call_counts[tool] if now - t < 60]
    if len(call_counts[tool]) >= 10:  # Max 10 calls per minute
        return {"hookSpecificOutput": {
            "hookEventName": input_data["hook_event_name"],
            "permissionDecision": "deny",
            "permissionDecisionReason": f"Rate limit: {tool} called {len(call_counts[tool])} times in last 60s",
        }}
    call_counts[tool].append(now)
    return {}

hooks = {"PreToolUse": [HookMatcher(hooks=[rate_limit])]}
```

### Chaining Order

Hooks execute in order. First deny wins.

```python
hooks = {
    "PreToolUse": [
        HookMatcher(hooks=[rate_limiter]),        # 1. Rate limit
        HookMatcher(hooks=[auth_check]),           # 2. Authorization
        HookMatcher(hooks=[input_sanitizer]),      # 3. Sanitize
        HookMatcher(matcher="Bash", hooks=[cmd_filter]),  # 4. Command filter (Bash only)
        HookMatcher(hooks=[audit_logger]),         # 5. Audit log
    ]
}
```

**Precedence:** Deny > Ask > Allow > Default (Ask)

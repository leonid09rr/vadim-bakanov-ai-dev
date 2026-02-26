# Spec Templates

Templates for spec-driven development. Copy to `_specs/{feature-name}/` and fill in.

| Template | Purpose | When to use |
|----------|---------|-------------|
| `user-spec.md` | User requirements (Russian, for humans) | Before starting any feature |
| `tech-spec.md` | Technical plan (English, for agents) | After user-spec approved |
| `task.md` | Atomic work unit with TDD anchors | After tech-spec decomposed |

## Workflow

```
user-spec.md (what & why)
    -> tech-spec.md (how)
        -> task-1.md, task-2.md, ... (atomic work)
```

Source: adapted from [molyanov-ai-dev](https://github.com/nickspaargaren/molyanov-ai-dev) (MIT)

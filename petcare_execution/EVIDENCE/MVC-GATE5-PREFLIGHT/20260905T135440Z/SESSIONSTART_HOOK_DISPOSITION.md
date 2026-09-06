# SessionStart hook failure — disposition

```
SESSIONSTART_HOOK_STATUS      = FAILED_NONBLOCKING
SESSIONSTART_HOOK_GATE5_IMPACT = NONE
CLASSIFICATION                = TOOLING_NONCRITICAL
```

## The hook that failed

Plugin `episodic-memory` 1.4.2, matcher `startup|resume|clear`:

```
node "${CLAUDE_PLUGIN_ROOT}/cli/episodic-memory.js" sync --background
```

Defined in
`~/.claude/plugins/cache/superpowers-marketplace/episodic-memory/1.4.2/hooks/hooks.json`.
Not a project hook: `.claude/settings.local.json` in this repository declares
`permissions` only and no `hooks` key; there is no `.claude/settings.json` and
no repository `CLAUDE.md`.

## Exact cause — reproduced, not inferred

```
Error [ERR_MODULE_NOT_FOUND]: Cannot find package '@anthropic-ai/claude-agent-sdk'
  imported from .../episodic-memory/1.4.2/dist/summarizer.js
  at packageResolve (node:internal/modules/esm/resolve:873:9)
Node.js v20.20.0
```

A missing runtime dependency in the plugin's own cache directory — the plugin
ships `dist/` but its `node_modules` are absent. The same plugin's MCP server
also failed to connect this session, which is the same defect seen twice.

## Why it is not a Gate-5 control

The hook syncs conversation history for episodic recall. It asserts nothing
about this repository. Primary evidence: a repository-wide search for
`episodic-memory` and `SessionStart` across all tracked `*.md`, `*.json` and
`*.sh` returns **zero** matches, so no MyVetiCare governance or safety
invariant is expressed through it. Every Gate-5 invariant below was
independently established under `bash` in this session.

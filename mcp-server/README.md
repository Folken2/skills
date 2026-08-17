# Nuvel Skills MCP Server

An MCP stdio server that exposes the Nuvel Skills hub — 50+ executable SOPs for
AI agents — as MCP resources and tools. Pure Python 3 stdlib, no external
dependencies.

## Usage

Run the server:

```bash
python3 mcp-server/skill_server.py
```

The server speaks [JSON-RPC 2.0](https://www.jsonrpc.org/specification) over
stdio: MCP clients send one JSON request per line on stdin, and the server
replies with one JSON message per line on stdout. All logging goes to stderr so
stdout stays a clean protocol channel.

### Skills directory

The server locates the skills hub (the directory containing `index.json` and
`<theme>/<name>/SKILL.md`) via the `SKILLS_DIR` environment variable. If unset,
it defaults to the `skills/` directory next to this repo's `mcp-server/` folder.

### Claude Desktop config

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "nuvel-skills": {
      "command": "python3",
      "args": ["/path/to/skills/mcp-server/skill_server.py"],
      "env": {
        "SKILLS_DIR": "/path/to/skills"
      }
    }
  }
}
```

### Claude Code (CLI) config

Add the server via the CLI:

```bash
claude mcp add nuvel-skills \
  --env SKILLS_DIR=/path/to/skills \
  -- python3 /path/to/skills/mcp-server/skill_server.py
```

Or add it to `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "nuvel-skills": {
      "command": "python3",
      "args": ["/path/to/skills/mcp-server/skill_server.py"],
      "env": { "SKILLS_DIR": "/path/to/skills" }
    }
  }
}
```

### Cursor config

Add to `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (project):

```json
{
  "mcpServers": {
    "nuvel-skills": {
      "command": "python3",
      "args": ["/path/to/skills/mcp-server/skill_server.py"],
      "env": { "SKILLS_DIR": "/path/to/skills" }
    }
  }
}
```

### Generic MCP client

Any MCP client that supports stdio transport can launch the server with:

- **command:** `python3`
- **args:** `["/path/to/skills/mcp-server/skill_server.py"]`
- **env:** `SKILLS_DIR=/path/to/skills`

## Capabilities

On `initialize` the server negotiates protocol version `2024-11-05` and
advertises: `resources.list`, `resources.read`, `tools.list`, `tools.call`.

### Resources

- `skill://{theme}/{name}` — Full `SKILL.md` content (`text/markdown`) for any
  skill in the hub.

`resources/list` enumerates one resource per skill across every theme, each with
its `uri`, `name`, `description`, and `mimeType`.

### Tools

- **`search_skills`** — Search skills by keyword in name or description.
  - Input: `query` (string)
  - Returns: matching skill entries (`uri`, `theme`, `name`, `description`, `author`).
- **`get_skill`** — Get the full `SKILL.md` content plus metadata by name.
  - Input: `name` (string) — either `name` (e.g. `bug-triage`) or `theme/name`
    (e.g. `software-development/bug-triage`).
  - Returns: full `SKILL.md` content, parsed frontmatter metadata, and index
    fields.

## Protocol reference

| Method            | Purpose                                            |
| ----------------- | -------------------------------------------------- |
| `initialize`      | Capability negotiation.                            |
| `resources/list`  | List every skill as an MCP resource.               |
| `resources/read`  | Read a skill's `SKILL.md` by `skill://` URI.       |
| `tools/list`      | List available tools and their input schemas.      |
| `tools/call`      | Invoke `search_skills` or `get_skill`.             |

Errors are returned as JSON-RPC error objects (e.g. unknown skill, malformed
URI, or unknown tool → code `-32602`; unknown method → `-32601`; malformed JSON
→ `-32700`). Notifications (`notifications/initialized`, `$/cancelRequest`) are
accepted and produce no response. EOF on stdin triggers a graceful shutdown.

## Quick test

```bash
# initialize
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' \
  | python3 mcp-server/skill_server.py 2>/dev/null

# list resources
echo '{"jsonrpc":"2.0","id":2,"method":"resources/list","params":{}}' \
  | python3 mcp-server/skill_server.py 2>/dev/null

# read one skill
echo '{"jsonrpc":"2.0","id":3,"method":"resources/read","params":{"uri":"skill://software-development/bug-triage"}}' \
  | python3 mcp-server/skill_server.py 2>/dev/null
```

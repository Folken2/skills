#!/usr/bin/env python3
"""Nuvel Skills MCP stdio server.

Exposes the Nuvel Skills hub as MCP resources and tools over stdio using
JSON-RPC 2.0. Stdlib only, no external dependencies.

Protocol channel: stdout (one JSON message per line).
Logging channel:  stderr.

The skills directory (the one containing index.json and <theme>/<name>/SKILL.md)
is located via the SKILLS_DIR environment variable, falling back to the
``skills`` directory alongside this script's parent (repo layout).
"""

import json
import os
import sys

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "nuvel-skills", "version": "1.0.0"}

# JSON-RPC standard error codes.
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


def log(*args):
    """Diagnostics go to stderr so stdout stays a clean protocol channel."""
    print(*args, file=sys.stderr, flush=True)


def skills_dir():
    """Resolve the skills directory (contains index.json)."""
    env = os.environ.get("SKILLS_DIR")
    if env:
        return os.path.abspath(env)
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(here), "skills")


def index_path():
    return os.path.join(skills_dir(), "index.json")


def load_index():
    """Load and return the parsed index.json."""
    with open(index_path(), "r", encoding="utf-8") as f:
        return json.load(f)


def iter_entries(index):
    """Yield (theme, entry) for every skill across every theme."""
    for theme, entries in index.get("themes", {}).items():
        for entry in entries:
            yield theme, entry


def entry_skill_path(theme, entry):
    """Local absolute path to a skill's SKILL.md.

    Honors an explicit ``path`` field on the entry if present (resolved
    relative to the skills dir), otherwise derives ``<theme>/<name>/SKILL.md``.
    """
    path = entry.get("path")
    if path:
        # Explicit path may point at the SKILL.md or the skill directory.
        candidate = os.path.join(skills_dir(), path)
        if os.path.isdir(candidate):
            candidate = os.path.join(candidate, "SKILL.md")
        return candidate
    return os.path.join(skills_dir(), theme, entry["name"], "SKILL.md")


def parse_frontmatter(text):
    """Minimal YAML-frontmatter parser for simple ``key: value`` pairs.

    Returns a dict of the leading ``---`` fenced block (empty if none).
    Avoids a YAML dependency; nested structures are ignored.
    """
    meta = {}
    if not text.startswith("---"):
        return meta
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return meta
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line or line.startswith((" ", "\t", "-")):
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    return meta


# --- Method handlers ---------------------------------------------------------


def handle_initialize(params):
    return {
        "protocolVersion": PROTOCOL_VERSION,
        "capabilities": {
            "resources": {"list": True, "read": True},
            "tools": {"list": True, "call": True},
        },
        "serverInfo": SERVER_INFO,
    }


def handle_resources_list(params):
    index = load_index()
    resources = []
    for theme, entry in iter_entries(index):
        name = entry["name"]
        resources.append({
            "uri": "skill://{}/{}".format(theme, name),
            "name": name,
            "description": entry.get("description", ""),
            "mimeType": "text/markdown",
        })
    return {"resources": resources}


def _find_entry(index, theme, name):
    for t, entry in iter_entries(index):
        if t == theme and entry["name"] == name:
            return t, entry
    return None, None


def _parse_skill_uri(uri):
    """Parse ``skill://{theme}/{name}`` -> (theme, name) or raise ValueError."""
    prefix = "skill://"
    if not uri.startswith(prefix):
        raise ValueError("URI must start with 'skill://'")
    rest = uri[len(prefix):]
    parts = rest.split("/")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError("URI must be 'skill://{theme}/{name}'")
    return parts[0], parts[1]


class McpError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


def handle_resources_read(params):
    uri = params.get("uri")
    if not uri:
        raise McpError(INVALID_PARAMS, "Missing required param 'uri'")
    try:
        theme, name = _parse_skill_uri(uri)
    except ValueError as exc:
        raise McpError(INVALID_PARAMS, "Invalid skill URI: {}".format(exc))

    index = load_index()
    theme, entry = _find_entry(index, theme, name)
    if entry is None:
        raise McpError(INVALID_PARAMS, "Skill not found: {}".format(uri))

    path = entry_skill_path(theme, entry)
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        raise McpError(INVALID_PARAMS, "SKILL.md not available for {}".format(uri))

    return {
        "contents": [{
            "uri": uri,
            "mimeType": "text/markdown",
            "text": content,
        }]
    }


def handle_tools_list(params):
    return {
        "tools": [
            {
                "name": "search_skills",
                "description": "Search skills by keyword in name or description.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Keyword to match against skill name/description.",
                        }
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "get_skill",
                "description": "Get the full SKILL.md content and metadata for a skill by name or 'theme/name'.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Skill name (e.g. 'bug-triage') or 'theme/name'.",
                        }
                    },
                    "required": ["name"],
                },
            },
        ]
    }


def tool_search_skills(args):
    query = (args.get("query") or "").strip().lower()
    if not query:
        raise McpError(INVALID_PARAMS, "Missing required argument 'query'")
    index = load_index()
    matches = []
    for theme, entry in iter_entries(index):
        haystack = "{} {}".format(
            entry.get("name", ""), entry.get("description", "")
        ).lower()
        if query in haystack:
            matches.append({
                "uri": "skill://{}/{}".format(theme, entry["name"]),
                "theme": theme,
                "name": entry["name"],
                "description": entry.get("description", ""),
                "author": entry.get("author", ""),
            })
    return {"query": query, "count": len(matches), "results": matches}


def tool_get_skill(args):
    name = (args.get("name") or "").strip()
    if not name:
        raise McpError(INVALID_PARAMS, "Missing required argument 'name'")

    index = load_index()
    wanted_theme, wanted_name = (None, name)
    if "/" in name:
        wanted_theme, wanted_name = name.split("/", 1)

    found = None
    for theme, entry in iter_entries(index):
        if entry["name"] != wanted_name:
            continue
        if wanted_theme is not None and theme != wanted_theme:
            continue
        found = (theme, entry)
        break

    if found is None:
        raise McpError(INVALID_PARAMS, "Skill not found: {}".format(name))

    theme, entry = found
    path = entry_skill_path(theme, entry)
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        raise McpError(INVALID_PARAMS, "SKILL.md not available for {}".format(name))

    return {
        "uri": "skill://{}/{}".format(theme, entry["name"]),
        "theme": theme,
        "name": entry["name"],
        "description": entry.get("description", ""),
        "author": entry.get("author", ""),
        "metadata": parse_frontmatter(content),
        "content": content,
    }


def handle_tools_call(params):
    tool_name = params.get("name")
    args = params.get("arguments") or {}
    handlers = {
        "search_skills": tool_search_skills,
        "get_skill": tool_get_skill,
    }
    handler = handlers.get(tool_name)
    if handler is None:
        raise McpError(INVALID_PARAMS, "Unknown tool: {}".format(tool_name))
    result = handler(args)
    # MCP tool results wrap output as a list of content blocks.
    return {
        "content": [{
            "type": "text",
            "text": json.dumps(result, ensure_ascii=False),
        }],
        "isError": False,
    }


METHODS = {
    "initialize": handle_initialize,
    "resources/list": handle_resources_list,
    "resources/read": handle_resources_read,
    "tools/list": handle_tools_list,
    "tools/call": handle_tools_call,
}


def dispatch(message):
    """Handle a single decoded JSON-RPC message. Returns a response dict or None."""
    msg_id = message.get("id")
    method = message.get("method")

    # Notifications (no id) get no response; ack lifecycle ones silently.
    is_notification = "id" not in message
    if method is None:
        if is_notification:
            return None
        return error_response(msg_id, INVALID_REQUEST, "Missing 'method'")

    if method.startswith("notifications/") or method.startswith("$/"):
        # e.g. notifications/initialized, $/cancelRequest — no response.
        return None

    handler = METHODS.get(method)
    if handler is None:
        if is_notification:
            return None
        return error_response(msg_id, METHOD_NOT_FOUND, "Method not found: {}".format(method))

    params = message.get("params") or {}
    try:
        result = handler(params)
    except McpError as exc:
        log("McpError in {}: {}".format(method, exc.message))
        return error_response(msg_id, exc.code, exc.message)
    except Exception as exc:  # noqa: BLE001 - report as JSON-RPC internal error
        log("Internal error in {}: {}".format(method, exc))
        return error_response(msg_id, INTERNAL_ERROR, "Internal error: {}".format(exc))

    if is_notification:
        return None
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def error_response(msg_id, code, message):
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": code, "message": message},
    }


def write_message(message):
    sys.stdout.write(json.dumps(message, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main():
    log("nuvel-skills MCP server starting (skills_dir={})".format(skills_dir()))
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError as exc:
            log("Parse error: {}".format(exc))
            write_message(error_response(None, PARSE_ERROR, "Parse error"))
            continue

        response = dispatch(message)
        if response is not None:
            write_message(response)
    log("nuvel-skills MCP server: EOF on stdin, shutting down.")


if __name__ == "__main__":
    main()

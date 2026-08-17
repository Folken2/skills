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
import urllib.error
import urllib.request

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
            {
                "name": "propose_improvement",
                "description": (
                    "Propose an improvement to a skill after using it and finding "
                    "it drifted (outdated tooling, missing edge cases, wrong "
                    "assumptions). Files a structured GitHub issue for a curator "
                    "to review."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "skill_name": {
                            "type": "string",
                            "description": "Name of the skill being improved (e.g. 'bug-triage').",
                        },
                        "current_version": {
                            "type": "string",
                            "description": "Version from the SKILL.md frontmatter (e.g. '1.0.0').",
                        },
                        "issue": {
                            "type": "string",
                            "description": "What went wrong or what changed.",
                        },
                        "suggested_fix": {
                            "type": "string",
                            "description": "Proposed correction or addition.",
                        },
                        "harness": {
                            "type": "string",
                            "description": "Agent/harness you're running (e.g. 'claude-code', 'cursor', 'hermes').",
                        },
                    },
                    "required": ["skill_name", "current_version", "issue", "suggested_fix"],
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


GITHUB_REPO = "Folken2/skills"
GITHUB_ISSUES_URL = "https://api.github.com/repos/{}/issues".format(GITHUB_REPO)


def _summarize(text, limit=60):
    """One-line summary for the issue title (first line, truncated)."""
    first = (text or "").strip().splitlines()[0] if (text or "").strip() else ""
    if len(first) > limit:
        first = first[: limit - 1].rstrip() + "…"
    return first


def _improvement_issue(skill_name, current_version, issue, suggested_fix, harness):
    """Build the (title, body) for a skill-improvement GitHub issue."""
    title = "[Skill Improvement] {} v{} — {}".format(
        skill_name, current_version, _summarize(issue) or "improvement"
    )
    body = (
        "## Skill Improvement Proposal\n\n"
        "| Field | Value |\n"
        "| --- | --- |\n"
        "| **Skill** | `{skill}` |\n"
        "| **Current version** | `{version}` |\n"
        "| **Harness** | `{harness}` |\n\n"
        "### Issue — what went wrong or changed\n\n"
        "{issue}\n\n"
        "### Suggested fix\n\n"
        "{fix}\n\n"
        "---\n"
        "_Filed via the `propose_improvement` MCP tool. A curator will review "
        "and merge accepted improvements._\n"
    ).format(
        skill=skill_name,
        version=current_version,
        harness=harness,
        issue=issue.strip(),
        fix=suggested_fix.strip(),
    )
    return title, body


def tool_propose_improvement(args):
    skill_name = (args.get("skill_name") or "").strip()
    current_version = (args.get("current_version") or "").strip()
    issue = (args.get("issue") or "").strip()
    suggested_fix = (args.get("suggested_fix") or "").strip()
    harness = (args.get("harness") or "").strip() or "unknown"

    missing = [
        k
        for k, v in (
            ("skill_name", skill_name),
            ("current_version", current_version),
            ("issue", issue),
            ("suggested_fix", suggested_fix),
        )
        if not v
    ]
    if missing:
        raise McpError(
            INVALID_PARAMS,
            "Missing required argument(s): {}".format(", ".join(missing)),
        )

    title, body = _improvement_issue(
        skill_name, current_version, issue, suggested_fix, harness
    )

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        log("GitHub API not configured (no GITHUB_TOKEN). Improvement proposal:")
        log("  title: {}".format(title))
        log(body)
        return {
            "status": "logged",
            "message": "GitHub API not configured — improvement logged to stderr instead",
            "title": title,
            "body": body,
        }

    payload = json.dumps(
        {"title": title, "body": body, "labels": ["skill-improvement"]}
    ).encode("utf-8")
    request = urllib.request.Request(
        GITHUB_ISSUES_URL,
        data=payload,
        method="POST",
        headers={
            "Authorization": "Bearer {}".format(token),
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "nuvel-skills-mcp",
        },
    )
    try:
        with urllib.request.urlopen(request) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace") if exc.fp else str(exc)
        log("GitHub API error {}: {}".format(exc.code, detail))
        raise McpError(
            INTERNAL_ERROR,
            "GitHub API returned {}: {}".format(exc.code, detail),
        )
    except urllib.error.URLError as exc:
        log("GitHub API request failed: {}".format(exc))
        raise McpError(INTERNAL_ERROR, "GitHub API request failed: {}".format(exc))

    return {
        "status": "filed",
        "message": "Improvement proposal filed as GitHub issue",
        "issue_url": data.get("html_url"),
        "issue_number": data.get("number"),
        "title": title,
    }


def handle_tools_call(params):
    tool_name = params.get("name")
    args = params.get("arguments") or {}
    handlers = {
        "search_skills": tool_search_skills,
        "get_skill": tool_get_skill,
        "propose_improvement": tool_propose_improvement,
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

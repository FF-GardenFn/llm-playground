# MCP Addons Server

## Abstract

This Model Context Protocol (MCP) server provides controlled access to common developer command-line tools for AI clients. The server exposes ripgrep, git, and jq through a sandboxed interface that enforces workspace boundaries and prevents arbitrary command execution.

## Purpose

The MCP Addons Server bridges AI assistants with local development utilities while maintaining strict security boundaries. Rather than granting shell access, this server exposes a curated set of tools through the Model Context Protocol, enabling AI clients to perform code search, version control inspection, and JSON manipulation within a designated workspace.

This approach satisfies two competing requirements:
1. Providing AI assistants with access to powerful developer tools
2. Preventing arbitrary code execution and filesystem access

## Architecture

The server implements the Model Context Protocol specification and communicates via standard input/output (stdio transport). It spawns child processes for each tool invocation but constrains their execution environment through path validation and argument sanitization.

### Security Model

The server enforces security through multiple mechanisms:

**Workspace Sandboxing**: All file operations are constrained to `WORKSPACE_ROOT`, defined by the environment variable of the same name or defaulting to the current working directory. Path traversal attempts using `..` or absolute paths outside this root are rejected.

**No Shell Execution**: Tools are invoked directly as child processes without shell interpretation. This prevents command injection through metacharacters or command chaining.

**Argument Sanitization**: All user-provided arguments are type-checked and passed as discrete parameters to child processes, eliminating injection vectors.

**Explicit Tool Enumeration**: Only four predefined tools are exposed. The server cannot be instructed to execute arbitrary commands.

**Read-Only Operations**: All exposed tools perform read-only operations. No tool can modify files, commit changes, or alter system state.

## Tools Reference

### ripgrep_search

Searches file contents using ripgrep (rg) within the workspace boundary.

**Parameters:**
- `pattern` (string, required): Regular expression pattern to search for
- `path` (string, optional): Relative path within workspace to search (defaults to workspace root)
- `max_results` (number, optional): Maximum number of matches per file

**Behavior:**
Executes `rg --line-number --no-heading [--max-count N] PATTERN PATH` within the resolved workspace path.

**Returns:**
Matching lines with line numbers, or "(no matches)" if the pattern is not found.

**Example:**
```json
{
  "pattern": "function\\s+\\w+",
  "path": "src",
  "max_results": 10
}
```

### git_status

Reports Git working tree status in porcelain format.

**Parameters:**
None

**Behavior:**
Executes `git status --porcelain=v1` in the workspace root.

**Returns:**
Machine-readable status output showing modified, added, deleted, and untracked files, or "(clean)" if no changes exist.

**Output Format:**
```
 M modified-file.ts
A  new-file.ts
?? untracked-file.ts
```

### git_grep

Searches Git-tracked files using git's native search capabilities.

**Parameters:**
- `pattern` (string, required): Regular expression pattern to search for

**Behavior:**
Executes `git grep -n PATTERN` across all tracked files in the repository.

**Returns:**
Matching lines prefixed with filename and line number, or "(no matches)" if the pattern is not found.

**Advantages over ripgrep_search:**
- Only searches tracked files (ignores .gitignore entries)
- Respects .gitattributes
- Faster for large repositories with many ignored files

**Example:**
```json
{
  "pattern": "TODO:"
}
```

### jq_filter

Filters and transforms JSON data using jq.

**Parameters:**
- `json` (string, required): JSON input to process
- `filter` (string, required): jq filter expression

**Behavior:**
Executes `jq FILTER` with the JSON input provided via stdin. This tool operates in-memory and does not access the filesystem.

**Returns:**
Filtered JSON output as a string.

**Example:**
```json
{
  "json": "{\"users\":[{\"name\":\"Alice\",\"age\":30},{\"name\":\"Bob\",\"age\":25}]}",
  "filter": ".users[] | select(.age > 26)"
}
```

**Output:**
```json
{
  "name": "Alice",
  "age": 30
}
```

## Installation

### Prerequisites

The following tools must be installed and available in the system PATH:

- Node.js 18 or later
- ripgrep (rg)
- git
- jq

On macOS:
```bash
brew install ripgrep git jq
```

On Ubuntu/Debian:
```bash
apt-get install ripgrep git jq
```

### Build

```bash
npm install
npm run build
```

The compiled server will be output to `dist/server.js`.

## Configuration

### Environment Variables

**WORKSPACE_ROOT** (required): Absolute path to the workspace directory. All file operations are constrained to this directory and its descendants.

**PORT** (optional): Port number for TCP transport (default: stdio transport)

### MCP Client Configuration

Add the following configuration to your MCP client (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "addons": {
      "command": "node",
      "args": [
        "/absolute/path/to/mcp-addons-server/dist/server.js"
      ],
      "env": {
        "WORKSPACE_ROOT": "/absolute/path/to/your/workspace"
      }
    }
  }
}
```

**Critical**: Replace both placeholder paths with actual absolute paths:
1. Path to the compiled server.js
2. Path to your workspace directory

## Usage

### Starting the Server

For development with automatic recompilation:
```bash
WORKSPACE_ROOT=/path/to/workspace npm run dev
```

For production:
```bash
WORKSPACE_ROOT=/path/to/workspace npm start
```

### Integration with AI Clients

Once configured, AI clients connected via MCP can invoke the exposed tools. The server handles tool discovery through MCP's capability negotiation.

Example interaction flow:
1. AI client requests available tools via MCP
2. Server responds with tool definitions including parameter schemas
3. AI client invokes tool with parameters
4. Server validates parameters, executes tool, returns results
5. AI client processes results and may invoke additional tools

### Verification

After starting the server, verify the workspace root in the console output:
```
[mcp-addons-server] started (stdio transport). WORKSPACE_ROOT=/path/to/workspace
```

## Security Considerations

### Path Traversal Protection

The `resolveInRoot` function enforces workspace boundaries:

```typescript
function resolveInRoot(p: string): string {
  const abs = path.resolve(WORKSPACE_ROOT, p || ".");
  const rel = path.relative(WORKSPACE_ROOT, abs);
  if (rel.startsWith("..") || path.isAbsolute(rel)) {
    throw new Error(`Path escapes WORKSPACE_ROOT: ${p}`);
  }
  return abs;
}
```

Attempts to access `../../../etc/passwd` or `/etc/passwd` will be rejected.

### Tool Isolation

Each tool spawns an isolated child process. The process cannot:
- Execute shell commands
- Chain multiple commands
- Access environment variables beyond those explicitly passed
- Write to the filesystem (all tools are read-only)

### Recommended Practices

1. Set `WORKSPACE_ROOT` to the minimum necessary directory scope
2. Run the server with minimal user privileges
3. Monitor server logs for rejected path traversal attempts
4. Regularly update dependencies to address security vulnerabilities
5. Do not expose this server to untrusted networks (stdio transport only)

## Limitations

- **Tool Availability**: All four tools (rg, git, jq) must be installed. Missing tools will cause runtime errors.
- **Performance**: Large repositories may experience latency on comprehensive searches.
- **Git Requirements**: Git tools require the workspace to be a valid Git repository.
- **No Write Operations**: The server provides read-only access. Committing changes or modifying files requires separate mechanisms.

## Version

Current version: 0.1.0

## License

MIT

## References

- Model Context Protocol Specification: https://modelcontextprotocol.io
- ripgrep: https://github.com/BurntSushi/ripgrep
- jq: https://jqlang.github.io/jq/

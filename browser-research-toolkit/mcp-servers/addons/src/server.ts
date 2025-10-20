import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import { spawn } from "node:child_process";
import path from "node:path";
import process from "node:process";

const WORKSPACE_ROOT = process.env.WORKSPACE_ROOT || process.cwd();

function resolveInRoot(p: string): string {
  const abs = path.resolve(WORKSPACE_ROOT, p || ".");
  const rel = path.relative(WORKSPACE_ROOT, abs);
  if (rel.startsWith("..") || path.isAbsolute(rel)) {
    throw new Error(`Path escapes WORKSPACE_ROOT: ${p}`);
  }
  return abs;
}

function run(
  cmd: string,
  args: string[],
  cwd?: string
): Promise<{ code: number; stdout: string; stderr: string }> {
  return new Promise((resolve) => {
    const proc = spawn(cmd, args, { cwd: cwd || WORKSPACE_ROOT });
    let out = "",
      err = "";
    proc.stdout.on("data", (d) => (out += d.toString()));
    proc.stderr.on("data", (d) => (err += d.toString()));
    proc.on("close", (code) =>
      resolve({ code: code ?? 0, stdout: out, stderr: err })
    );
  });
}

const TOOLS: Tool[] = [
  {
    name: "ripgrep_search",
    description: "Search code with ripgrep (rg) within WORKSPACE_ROOT.",
    inputSchema: {
      type: "object",
      properties: {
        pattern: { type: "string", description: "Regex pattern to search" },
        path: { type: "string", description: "Path within WORKSPACE_ROOT" },
        max_results: { type: "number", description: "Max matches per file" },
      },
      required: ["pattern"],
    },
  },
  {
    name: "git_status",
    description: "Git porcelain status in WORKSPACE_ROOT.",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "git_grep",
    description: "Search tracked files using git grep.",
    inputSchema: {
      type: "object",
      properties: {
        pattern: { type: "string", description: "Pattern to search" },
      },
      required: ["pattern"],
    },
  },
  {
    name: "jq_filter",
    description: "Filter JSON using jq. Returns filtered JSON string.",
    inputSchema: {
      type: "object",
      properties: {
        json: { type: "string", description: "Input JSON string" },
        filter: { type: "string", description: "jq filter expression" },
      },
      required: ["json", "filter"],
    },
  },
];

const server = new Server(
  {
    name: "mcp-addons-server",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: TOOLS,
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "ripgrep_search": {
        const p = resolveInRoot((args?.path as string) ?? ".");
        const flags = ["--line-number", "--no-heading"];
        const maxResults = args?.max_results as number | undefined;
        if (maxResults) flags.push("--max-count", String(maxResults));
        const { code, stdout, stderr } = await run("rg", [
          ...flags,
          String(args?.pattern),
          p,
        ]);
        if (code !== 0 && !stdout) {
          return {
            content: [
              {
                type: "text",
                text: `rg failed: ${stderr || "no matches or rg not installed"}`,
              },
            ],
            isError: true,
          };
        }
        return {
          content: [{ type: "text", text: stdout || "(no matches)" }],
        };
      }

      case "git_status": {
        const { code, stdout, stderr } = await run("git", [
          "status",
          "--porcelain=v1",
        ]);
        if (code !== 0) {
          return {
            content: [
              { type: "text", text: `git status failed: ${stderr}` },
            ],
            isError: true,
          };
        }
        return {
          content: [{ type: "text", text: stdout || "(clean)" }],
        };
      }

      case "git_grep": {
        const { code, stdout, stderr } = await run("git", [
          "grep",
          "-n",
          String(args?.pattern),
        ]);
        if (code !== 0 && !stdout) {
          return {
            content: [
              {
                type: "text",
                text: `git grep failed: ${
                  stderr || "no matches or git not installed"
                }`,
              },
            ],
            isError: true,
          };
        }
        return {
          content: [{ type: "text", text: stdout || "(no matches)" }],
        };
      }

      case "jq_filter": {
        const { code, stdout, stderr } = await new Promise<{
          code: number;
          stdout: string;
          stderr: string;
        }>((resolve) => {
          const proc = spawn("jq", [String(args?.filter)]);
          let out = "",
            err = "";
          proc.stdout.on("data", (d) => (out += d.toString()));
          proc.stderr.on("data", (d) => (err += d.toString()));
          proc.on("close", (c) =>
            resolve({ code: c ?? 0, stdout: out, stderr: err })
          );
          proc.stdin.write(String(args?.json));
          proc.stdin.end();
        });
        if (code !== 0) {
          return {
            content: [
              {
                type: "text",
                text: `jq failed: ${
                  stderr || "jq not installed or bad filter"
                }`,
              },
            ],
            isError: true,
          };
        }
        return {
          content: [{ type: "text", text: stdout.trim() }],
        };
      }

      default:
        return {
          content: [{ type: "text", text: `Unknown tool: ${name}` }],
          isError: true,
        };
    }
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: `Error: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error(
    `[mcp-addons-server] started (stdio). WORKSPACE_ROOT=${WORKSPACE_ROOT}`
  );
}

main().catch(console.error);

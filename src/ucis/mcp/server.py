"""
PyUCIS MCP Server

Model Context Protocol server for UCIS coverage database access.
"""
import asyncio
import sys
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .db_manager import DatabaseManager
from .tools import ToolImplementations


# Server instance
app = Server("pyucis-mcp-server")
db_manager = DatabaseManager()
tools = ToolImplementations(db_manager)


# Tool definitions
TOOLS = [
    Tool(
        name="open_database",
        description="Open a UCIS coverage database for analysis",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the UCIS database file"
                },
                "format": {
                    "type": "string",
                    "description": "Database format (xml, yaml, ucis). Auto-detect if omitted.",
                    "enum": ["xml", "yaml", "ucis"]
                }
            },
            "required": ["path"]
        }
    ),
    Tool(
        name="close_database",
        description="Close an open UCIS database",
        inputSchema={
            "type": "object",
            "properties": {
                "db_id": {
                    "type": "string",
                    "description": "Database ID to close"
                }
            },
            "required": ["db_id"]
        }
    ),
    Tool(
        name="list_databases",
        description="List all currently open UCIS databases",
        inputSchema={
            "type": "object",
            "properties": {}
        }
    ),
    Tool(
        name="get_database_info",
        description="Get detailed information about a database",
        inputSchema={
            "type": "object",
            "properties": {
                "db_id": {
                    "type": "string",
                    "description": "Database ID"
                }
            },
            "required": ["db_id"]
        }
    ),
    Tool(
        name="get_coverage_summary",
        description="Get overall coverage summary with percentages by type",
        inputSchema={
            "type": "object",
            "properties": {
                "db_id": {
                    "type": "string",
                    "description": "Database ID"
                }
            },
            "required": ["db_id"]
        }
    ),
    Tool(
        name="get_coverage_gaps",
        description="Identify coverage gaps (uncovered or low-coverage items)",
        inputSchema={
            "type": "object",
            "properties": {
                "db_id": {
                    "type": "string",
                    "description": "Database ID"
                },
                "threshold": {
                    "type": "number",
                    "description": "Coverage threshold (0-100). Items below this are shown."
                }
            },
            "required": ["db_id"]
        }
    ),
    Tool(
        name="get_covergroups",
        description="Get covergroup information with optional bin details",
        inputSchema={
            "type": "object",
            "properties": {
                "db_id": {
                    "type": "string",
                    "description": "Database ID"
                },
                "include_bins": {
                    "type": "boolean",
                    "description": "Include detailed bin information"
                }
            },
            "required": ["db_id"]
        }
    ),
    Tool(
        name="get_tests",
        description="Get test execution information (pass/fail, timestamps, etc.)",
        inputSchema={
            "type": "object",
            "properties": {
                "db_id": {
                    "type": "string",
                    "description": "Database ID"
                }
            },
            "required": ["db_id"]
        }
    ),
    Tool(
        name="get_hierarchy",
        description="Get design hierarchy structure",
        inputSchema={
            "type": "object",
            "properties": {
                "db_id": {
                    "type": "string",
                    "description": "Database ID"
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Maximum depth to traverse"
                }
            },
            "required": ["db_id"]
        }
    ),
    Tool(
        name="get_metrics",
        description="Get coverage metrics and statistics with analysis",
        inputSchema={
            "type": "object",
            "properties": {
                "db_id": {
                    "type": "string",
                    "description": "Database ID"
                }
            },
            "required": ["db_id"]
        }
    ),
    Tool(
        name="get_bins",
        description="Get bin-level coverage details with filtering options",
        inputSchema={
            "type": "object",
            "properties": {
                "db_id": {
                    "type": "string",
                    "description": "Database ID"
                },
                "covergroup": {
                    "type": "string",
                    "description": "Filter by covergroup name"
                },
                "coverpoint": {
                    "type": "string",
                    "description": "Filter by coverpoint name"
                },
                "min_hits": {
                    "type": "integer",
                    "description": "Minimum hit count"
                },
                "max_hits": {
                    "type": "integer",
                    "description": "Maximum hit count"
                },
                "sort_by": {
                    "type": "string",
                    "description": "Sort by 'count' or 'name'",
                    "enum": ["count", "name"]
                }
            },
            "required": ["db_id"]
        }
    ),
    Tool(
        name="compare_databases",
        description="Compare two UCIS databases to identify differences",
        inputSchema={
            "type": "object",
            "properties": {
                "db_id": {
                    "type": "string",
                    "description": "Baseline database ID"
                },
                "compare_db_id": {
                    "type": "string",
                    "description": "Comparison database ID"
                }
            },
            "required": ["db_id", "compare_db_id"]
        }
    ),
    Tool(
        name="get_hotspots",
        description="Identify coverage hotspots and high-value targets",
        inputSchema={
            "type": "object",
            "properties": {
                "db_id": {
                    "type": "string",
                    "description": "Database ID"
                },
                "threshold": {
                    "type": "number",
                    "description": "Coverage threshold (default: 80)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum items per category (default: 10)"
                }
            },
            "required": ["db_id"]
        }
    ),
    Tool(
        name="get_code_coverage",
        description="Get code coverage with multiple export format support",
        inputSchema={
            "type": "object",
            "properties": {
                "db_id": {
                    "type": "string",
                    "description": "Database ID"
                },
                "output_format": {
                    "type": "string",
                    "description": "Output format",
                    "enum": ["json", "lcov", "cobertura", "jacoco", "clover"]
                }
            },
            "required": ["db_id"]
        }
    ),
    Tool(
        name="get_assertions",
        description="Get assertion coverage (SVA/PSL)",
        inputSchema={
            "type": "object",
            "properties": {
                "db_id": {
                    "type": "string",
                    "description": "Database ID"
                }
            },
            "required": ["db_id"]
        }
    ),
    Tool(
        name="get_toggle_coverage",
        description="Get signal toggle coverage information",
        inputSchema={
            "type": "object",
            "properties": {
                "db_id": {
                    "type": "string",
                    "description": "Database ID"
                }
            },
            "required": ["db_id"]
        }
    ),
]


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Call a tool with given arguments."""
    try:
        # Route to appropriate tool implementation
        if name == "open_database":
            result = await tools.open_database(
                arguments.get("path"),
                arguments.get("format")
            )
        elif name == "close_database":
            result = await tools.close_database(arguments["db_id"])
        elif name == "list_databases":
            result = await tools.list_databases()
        elif name == "get_database_info":
            result = await tools.get_database_info(arguments["db_id"])
        elif name == "get_coverage_summary":
            result = await tools.get_coverage_summary(arguments["db_id"])
        elif name == "get_coverage_gaps":
            result = await tools.get_coverage_gaps(
                arguments["db_id"],
                arguments.get("threshold")
            )
        elif name == "get_covergroups":
            result = await tools.get_covergroups(
                arguments["db_id"],
                arguments.get("include_bins", False)
            )
        elif name == "get_tests":
            result = await tools.get_tests(arguments["db_id"])
        elif name == "get_hierarchy":
            result = await tools.get_hierarchy(
                arguments["db_id"],
                arguments.get("max_depth")
            )
        elif name == "get_metrics":
            result = await tools.get_metrics(arguments["db_id"])
        elif name == "get_bins":
            result = await tools.get_bins(
                arguments["db_id"],
                arguments.get("covergroup"),
                arguments.get("coverpoint"),
                arguments.get("min_hits"),
                arguments.get("max_hits"),
                arguments.get("sort_by")
            )
        elif name == "compare_databases":
            result = await tools.compare_databases(
                arguments["db_id"],
                arguments["compare_db_id"]
            )
        elif name == "get_hotspots":
            result = await tools.get_hotspots(
                arguments["db_id"],
                arguments.get("threshold", 80.0),
                arguments.get("limit", 10)
            )
        elif name == "get_code_coverage":
            result = await tools.get_code_coverage(
                arguments["db_id"],
                arguments.get("output_format", "json")
            )
        elif name == "get_assertions":
            result = await tools.get_assertions(arguments["db_id"])
        elif name == "get_toggle_coverage":
            result = await tools.get_toggle_coverage(arguments["db_id"])
        else:
            result = {"success": False, "error": f"Unknown tool: {name}"}
        
        # Format result as JSON
        import json
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    except Exception as e:
        import json
        error_result = {"success": False, "error": str(e)}
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]


async def run_server():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def main():
    """Entry point for the MCP server."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # Cleanup
        db_manager.close_all()


if __name__ == "__main__":
    main()

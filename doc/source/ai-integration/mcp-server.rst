##########
MCP Server
##########

The PyUCIS MCP server lets AI assistants (such as Claude) query your coverage
databases using natural language. Instead of memorizing command syntax, you
can ask questions like:

* *"What is the overall coverage of my regression?"*
* *"Which covergroups have the lowest coverage?"*
* *"Show me all bins that were never hit."*
* *"Compare today's run to yesterday's baseline and report any regressions."*
* *"Export coverage as LCOV and tell me what genhtml command to run."*

The server uses the `Model Context Protocol (MCP) <https://modelcontextprotocol.io/>`_,
a standard interface for connecting AI tools to external data sources.

Installation
============

.. code-block:: bash

    pip install pyucis[dev]

This installs the ``pyucis-mcp-server`` command and its dependencies.

Configuring Claude Desktop
==========================

1. Find your Claude Desktop config file:

   * **macOS**: ``~/Library/Application Support/Claude/claude_desktop_config.json``
   * **Linux**: ``~/.config/Claude/claude_desktop_config.json``
   * **Windows**: ``%APPDATA%\Claude\claude_desktop_config.json``

2. Add the PyUCIS server entry:

   .. code-block:: json

       {
         "mcpServers": {
           "pyucis": {
             "command": "pyucis-mcp-server"
           }
         }
       }

3. Restart Claude Desktop.

The PyUCIS tools are now available in your conversations.

Example Session
===============

Once connected, open a coverage database by telling Claude the file path, then ask
questions in plain English:

.. code-block:: text

    You: Open /path/to/regression.xml and give me a coverage summary.

    Claude: The database has 78.4% overall coverage across 142 covergroups.
            Functional coverage is 81.2%; code coverage is 74.6%.
            There are 23 covergroups below 50%.

    You: Which covergroups have zero coverage?

    Claude: The following 8 covergroups have 0% coverage: ...

    You: Compare this to /path/to/baseline.xml and report regressions.

    Claude: Compared to baseline, 3 items regressed: ...

Available Operations
====================

The MCP server provides tools for:

* Opening, listing, and closing databases
* Coverage summary, gaps, and metrics
* Covergroup, coverpoint, and bin details
* Design hierarchy navigation
* Test execution history
* Database comparison (regression detection)
* Hotspot analysis
* Code coverage export (LCOV, Cobertura, JaCoCo, Clover)
* Assertion and toggle coverage

Starting the Server Manually
============================

The server communicates via stdin/stdout and is normally started by the MCP
client automatically. To start it manually for testing:

.. code-block:: bash

    pyucis-mcp-server

See the `MCP specification <https://modelcontextprotocol.io/>`_ for client
integration details beyond Claude Desktop.

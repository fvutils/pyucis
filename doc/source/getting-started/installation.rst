############
Installation
############

Requirements
============

* Python 3.8 or later
* Linux, macOS, or Windows

Basic Install
=============

.. code-block:: bash

    pip install pyucis

This installs the ``ucis`` command-line tool and all core library functionality.

With MCP Server Support
=======================

To enable the :doc:`../ai-integration/mcp-server` for AI assistant integration:

.. code-block:: bash

    pip install pyucis[dev]

This adds the ``pyucis-mcp-server`` command and its dependencies
(``mcp``, ``lxml``, ``pyyaml``, ``jsonschema``).

Verify the Install
==================

.. code-block:: bash

    ucis --help

You should see the list of available sub-commands.

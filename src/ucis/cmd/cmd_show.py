"""
Show Command Dispatcher

Dispatches to specific show command implementations.
"""
from ucis.cmd.show.show_summary import ShowSummary
from ucis.cmd.show.show_gaps import ShowGaps
from ucis.cmd.show.show_covergroups import ShowCovergroups
from ucis.cmd.show.show_bins import ShowBins
from ucis.cmd.show.show_tests import ShowTests
from ucis.cmd.show.show_hierarchy import ShowHierarchy
from ucis.cmd.show.show_metrics import ShowMetrics
from ucis.cmd.show.show_compare import ShowCompare
from ucis.cmd.show.show_hotspots import ShowHotspots
from ucis.cmd.show.show_code_coverage import ShowCodeCoverage
from ucis.cmd.show.show_assertions import ShowAssertions
from ucis.cmd.show.show_toggle import ShowToggle


def show(args):
    """
    Dispatcher for show commands.
    
    Args:
        args: Parsed command-line arguments with 'show_cmd' attribute
    """
    # Map of show subcommands to their implementations
    show_commands = {
        'summary': ShowSummary,
        'gaps': ShowGaps,
        'covergroups': ShowCovergroups,
        'bins': ShowBins,
        'tests': ShowTests,
        'hierarchy': ShowHierarchy,
        'metrics': ShowMetrics,
        'compare': ShowCompare,
        'hotspots': ShowHotspots,
        'code-coverage': ShowCodeCoverage,
        'assertions': ShowAssertions,
        'toggle': ShowToggle,
    }
    
    show_cmd = args.show_cmd
    
    if show_cmd not in show_commands:
        raise Exception(f"Unknown show command: {show_cmd}")
    
    # Instantiate and execute the command
    cmd_class = show_commands[show_cmd]
    cmd = cmd_class(args)
    cmd.execute()

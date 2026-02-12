'''
Created on Jun 11, 2022

@author: mballance
'''
import argparse
from ucis.cmd import cmd_list_db_formats
from ucis.cmd import cmd_list_report_formats
from ucis.cmd import cmd_report, cmd_merge, cmd_convert, cmd_show
import sys
import traceback
import os

def get_parser():
    parser = argparse.ArgumentParser(description="Manipulate UCIS coverage data")
    parser.prog = "ucis"
    
    subparser = parser.add_subparsers()
    subparser.required = True

    convert = subparser.add_parser("convert",
        help="""
        Converts coverage data from one format to another
        """)
    convert.add_argument("--out", "-o",
        help="Specifies the output of the conversion",
        required=True)
    convert.add_argument("--input-format", "-if",
        help="Specifies the format of the input database. Defaults to 'xml'")
    convert.add_argument("--output-format", "-of",
        help="Specifies the format of the output database. Defaults to 'xml'")
    convert.add_argument("input", help="Source database to convert")
    convert.set_defaults(func=cmd_convert.convert)
   
    merge = subparser.add_parser("merge",
        help="""
        Merges coverage data from two or more databases into a single merged database
        """)
    merge.add_argument("--out", "-o", 
        help="Specifies the output of the merge",
        required=True)
    merge.add_argument("--input-format", "-if",
        help="Specifies the format of the input databases. Defaults to 'xml'")
    merge.add_argument("--output-format", "-of",
        help="Specifies the format of the input databases. Defaults to 'xml'")
    merge.add_argument("--libucis", "-l",
        help="Specifies the name/path of the UCIS shared library")
    merge.add_argument("--squash-history",
        action="store_true",
        default=False,
        help="Collapse per-test history into a single summary node")
    merge.add_argument("db", nargs="+")
    merge.set_defaults(func=cmd_merge.merge)
    
    list_db_formats = subparser.add_parser("list-db-formats",
        help="Shows available database formats")
    list_db_formats.set_defaults(func=cmd_list_db_formats.list_db_formats)
    
    list_rpt_formats = subparser.add_parser("list-rpt-formats",
        help="Shows available report filters")
    list_rpt_formats.set_defaults(func=cmd_list_report_formats.list_report_formats)
    
    report = subparser.add_parser("report",
        help="Generate a report (typically textual) from coverage data")
    report.add_argument("--out", "-o",
        help="Specifies the output location for the report")
    report.add_argument("--input-format", "-if",
        help="Specifies the format of the input database. Defaults to 'xml'")
    report.add_argument("--output-format", "-of",
        help="Specifies the output format of the report. Defaults to 'txt'")
    report.add_argument("db", help="Path to the coverage database")
    report.set_defaults(func=cmd_report.report)

    show = subparser.add_parser("show",
        help="Query and display coverage information from UCIS database")
    show_subparser = show.add_subparsers(dest='show_cmd')
    show_subparser.required = True
    
    # show summary subcommand
    show_summary = show_subparser.add_parser("summary",
        help="Display overall coverage summary")
    show_summary.add_argument("--out", "-o",
        help="Specifies the output location for the report")
    show_summary.add_argument("--input-format", "-if",
        help="Specifies the format of the input database. Defaults to 'xml'")
    show_summary.add_argument("--output-format", "-of",
        help="Specifies the output format. Defaults to 'json'",
        default='json',
        choices=['json', 'text', 'txt'])
    show_summary.add_argument("db", help="Path to the coverage database")
    
    # show gaps subcommand
    show_gaps = show_subparser.add_parser("gaps",
        help="Display coverage gaps (uncovered bins and coverpoints)")
    show_gaps.add_argument("--out", "-o",
        help="Specifies the output location for the report")
    show_gaps.add_argument("--input-format", "-if",
        help="Specifies the format of the input database. Defaults to 'xml'")
    show_gaps.add_argument("--output-format", "-of",
        help="Specifies the output format. Defaults to 'json'",
        default='json',
        choices=['json', 'text', 'txt'])
    show_gaps.add_argument("--threshold", "-t",
        help="Only show coverpoints with coverage below this threshold (0-100)",
        type=float,
        default=None)
    show_gaps.add_argument("db", help="Path to the coverage database")
    
    # show covergroups subcommand
    show_covergroups = show_subparser.add_parser("covergroups",
        help="Display detailed covergroup information")
    show_covergroups.add_argument("--out", "-o",
        help="Specifies the output location for the report")
    show_covergroups.add_argument("--input-format", "-if",
        help="Specifies the format of the input database. Defaults to 'xml'")
    show_covergroups.add_argument("--output-format", "-of",
        help="Specifies the output format. Defaults to 'json'",
        default='json',
        choices=['json', 'text', 'txt'])
    show_covergroups.add_argument("--include-bins", "-b",
        help="Include detailed bin information",
        action='store_true',
        default=False)
    show_covergroups.add_argument("db", help="Path to the coverage database")
    
    # show bins subcommand
    show_bins = show_subparser.add_parser("bins",
        help="Display bin-level coverage details")
    show_bins.add_argument("--out", "-o",
        help="Specifies the output location for the report")
    show_bins.add_argument("--input-format", "-if",
        help="Specifies the format of the input database. Defaults to 'xml'")
    show_bins.add_argument("--output-format", "-of",
        help="Specifies the output format. Defaults to 'json'",
        default='json',
        choices=['json', 'text', 'txt'])
    show_bins.add_argument("--covergroup", "-cg",
        help="Filter by covergroup name")
    show_bins.add_argument("--coverpoint", "-cp",
        help="Filter by coverpoint name")
    show_bins.add_argument("--min-hits",
        help="Show only bins with at least this many hits",
        type=int,
        default=None)
    show_bins.add_argument("--max-hits",
        help="Show only bins with at most this many hits",
        type=int,
        default=None)
    show_bins.add_argument("--sort", "-s",
        help="Sort bins by 'count' or 'name'",
        choices=['count', 'name'],
        default=None)
    show_bins.add_argument("db", help="Path to the coverage database")
    
    # show tests subcommand
    show_tests = show_subparser.add_parser("tests",
        help="Display test execution information")
    show_tests.add_argument("--out", "-o",
        help="Specifies the output location for the report")
    show_tests.add_argument("--input-format", "-if",
        help="Specifies the format of the input database. Defaults to 'xml'")
    show_tests.add_argument("--output-format", "-of",
        help="Specifies the output format. Defaults to 'json'",
        default='json',
        choices=['json', 'text', 'txt'])
    show_tests.add_argument("db", help="Path to the coverage database")
    
    # show hierarchy subcommand
    show_hierarchy = show_subparser.add_parser("hierarchy",
        help="Display design hierarchy structure")
    show_hierarchy.add_argument("--out", "-o",
        help="Specifies the output location for the report")
    show_hierarchy.add_argument("--input-format", "-if",
        help="Specifies the format of the input database. Defaults to 'xml'")
    show_hierarchy.add_argument("--output-format", "-of",
        help="Specifies the output format. Defaults to 'json'",
        default='json',
        choices=['json', 'text', 'txt'])
    show_hierarchy.add_argument("--max-depth", "-d",
        help="Maximum depth to traverse",
        type=int,
        default=None)
    show_hierarchy.add_argument("db", help="Path to the coverage database")
    
    # show metrics subcommand
    show_metrics = show_subparser.add_parser("metrics",
        help="Display coverage metrics and statistics")
    show_metrics.add_argument("--out", "-o",
        help="Specifies the output location for the report")
    show_metrics.add_argument("--input-format", "-if",
        help="Specifies the format of the input database. Defaults to 'xml'")
    show_metrics.add_argument("--output-format", "-of",
        help="Specifies the output format. Defaults to 'json'",
        default='json',
        choices=['json', 'text', 'txt'])
    show_metrics.add_argument("db", help="Path to the coverage database")
    
    # show compare subcommand
    show_compare = show_subparser.add_parser("compare",
        help="Compare coverage between two databases")
    show_compare.add_argument("--out", "-o",
        help="Specifies the output location for the report")
    show_compare.add_argument("--input-format", "-if",
        help="Specifies the format of the input database. Defaults to 'xml'")
    show_compare.add_argument("--output-format", "-of",
        help="Specifies the output format. Defaults to 'json'",
        default='json',
        choices=['json', 'text', 'txt'])
    show_compare.add_argument("db", help="Path to the baseline coverage database")
    show_compare.add_argument("compare_db", help="Path to the comparison database")
    
    # show hotspots subcommand
    show_hotspots = show_subparser.add_parser("hotspots",
        help="Identify coverage hotspots and high-value targets")
    show_hotspots.add_argument("--out", "-o",
        help="Specifies the output location for the report")
    show_hotspots.add_argument("--input-format", "-if",
        help="Specifies the format of the input database. Defaults to 'xml'")
    show_hotspots.add_argument("--output-format", "-of",
        help="Specifies the output format. Defaults to 'json'",
        default='json',
        choices=['json', 'text', 'txt'])
    show_hotspots.add_argument("--threshold", "-t",
        help="Coverage threshold for low-coverage groups (default: 80)",
        type=float,
        default=80.0)
    show_hotspots.add_argument("--limit", "-l",
        help="Maximum number of items to show per category (default: 10)",
        type=int,
        default=10)
    show_hotspots.add_argument("db", help="Path to the coverage database")
    
    # show code-coverage subcommand
    show_code_cov = show_subparser.add_parser("code-coverage",
        help="Display code coverage with support for LCOV/Cobertura formats")
    show_code_cov.add_argument("--out", "-o",
        help="Specifies the output location for the report")
    show_code_cov.add_argument("--input-format", "-if",
        help="Specifies the format of the input database. Defaults to 'xml'")
    show_code_cov.add_argument("--output-format", "-of",
        help="Specifies the output format",
        default='json',
        choices=['json', 'text', 'txt', 'lcov', 'cobertura', 'jacoco', 'clover'])
    show_code_cov.add_argument("db", help="Path to the coverage database")
    
    # show assertions
    show_assertions = show_subparser.add_parser("assertions",
        help="Display assertion coverage information")
    show_assertions.add_argument("--out", "-o",
        help="Specifies the output location for the report")
    show_assertions.add_argument("--input-format", "-if",
        help="Specifies the format of the input database. Defaults to 'xml'")
    show_assertions.add_argument("--output-format", "-of",
        help="Specifies the output format",
        default='json',
        choices=['json', 'text', 'txt'])
    show_assertions.add_argument("db", help="Path to the coverage database")
    
    # show toggle
    show_toggle = show_subparser.add_parser("toggle",
        help="Display toggle coverage information")
    show_toggle.add_argument("--out", "-o",
        help="Specifies the output location for the report")
    show_toggle.add_argument("--input-format", "-if",
        help="Specifies the format of the input database. Defaults to 'xml'")
    show_toggle.add_argument("--output-format", "-of",
        help="Specifies the output format",
        default='json',
        choices=['json', 'text', 'txt'])
    show_toggle.add_argument("db", help="Path to the coverage database")
    
    show.set_defaults(func=cmd_show.show)

    
    return parser

def main():
    # Print skill information at the start
    print_skill_info()
    print()
    
    parser = get_parser()

    argv = []
    plusargs = []
    for arg in sys.argv[1:]:
        if arg[0] == '+':
            plusargs.append(arg)
        else:
            argv.append(arg)

    args = parser.parse_args(args=argv)
    setattr(args, "plusargs", plusargs)

    try:
        args.func(args)
    except Exception as e:
        traceback.print_exc()
        print("Error: %s" % "{0}".format(e))

def print_skill_info():
    """Print the absolute path to the PyUCIS AgentSkills file."""
    # Get the absolute path to the ucis module
    import ucis
    ucis_module_path = os.path.abspath(os.path.dirname(ucis.__file__))
    skill_path = os.path.join(ucis_module_path, "share", "SKILL.md")
    
    print("=" * 70)
    print("PyUCIS AgentSkills Information")
    print("=" * 70)
    print(f"\nSkill Definition: {skill_path}")
    print("\nNote for LLM Agents:")
    print("  This file contains detailed information about PyUCIS capabilities,")
    print("  usage patterns, and best practices. LLM agents should reference")
    print("  this skill to better understand how to work with UCIS coverage")
    print("  databases and leverage PyUCIS tools effectively.")
    print("\nFor more information, visit: https://agentskills.io")
    print("=" * 70)

if __name__ == "__main__":
    main()
    

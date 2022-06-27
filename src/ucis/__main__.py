'''
Created on Jun 11, 2022

@author: mballance
'''
import argparse
from ucis.cmd import cmd_list_db_formats
from ucis.cmd import cmd_list_report_formats
from .cmd import cmd_report
import sys

def get_parser():
    parser = argparse.ArgumentParser()
    
    subparser = parser.add_subparsers()
    subparser.required = True
   
    # merge = subparser.add_parser("merge")
    # merge.add_argument("--out", "-o", 
    #     help="Specifies the output of the merge",
    #     required=True)
    # merge.add_argument("--input-format", "-if",
    #     help="Specifies the format of the input databases. Defaults to 'xml'")
    # merge.add_argument("--output-format", "-of",
    #     help="Specifies the format of the input databases. Defaults to 'xml'")
    # merge.add_argument("--libucis", "-l",
    #     help="Specifies the name/path of the UCIS shared library")
    # merge.add_argument("db", action="append")
    # merge.set_defaults(func=cmd.cmd_merge.merge)
    
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

    
    return parser

def main():
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
        print("Error: %s" % "{0}".format(e))

if __name__ == "__main__":
    main()
    
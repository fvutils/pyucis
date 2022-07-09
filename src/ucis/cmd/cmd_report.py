'''
Created on Jun 22, 2022

@author: mballance
'''
from ucis.rgy.format_if_db import FormatIfDb
from ucis.rgy.format_if_rpt import FormatIfRpt
from ucis.rgy.format_rgy import FormatRgy

def report(args):
    rgy = FormatRgy.inst()

    if args.input_format is None:
        args.input_format = rgy.getDefaultDatabase()
        
    if args.output_format is None:
        args.output_format = rgy.getDefaultReport()

    if not rgy.hasDatabaseFormat(args.input_format):
        raise Exception("Unknown input format %s ; supported=%s" % (
            args.input_format, str(rgy.getDatabaseFormats())))
    if not rgy.hasReportFormat(args.output_format):
        raise Exception("Unknown report format %s ; supported=%s" % (
            args.output_format, str(rgy.getReportFormats())))

    input_desc = rgy.getDatabaseDesc(args.input_format)
    input_if : FormatIfDb = input_desc.fmt_if()
    output_desc = rgy.getReportDesc(args.output_format)
    output_if : FormatIfRpt = output_desc.fmt_if()

    in_db = input_if.read(args.db)

    with open(args.out, "w") as fp:
        output_if.report(in_db, fp, [])

    in_db.close()
        
#    in_desc = rgy.
    
    pass
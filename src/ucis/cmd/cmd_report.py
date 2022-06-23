'''
Created on Jun 22, 2022

@author: mballance
'''
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
        
#    in_desc = rgy.
    
    pass
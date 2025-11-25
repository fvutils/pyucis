'''
Created on Jun 11, 2022

@author: mballance
'''

from typing import List
from ucis.merge.db_merger import DbMerger
from ucis.rgy import FormatRgy
from ucis.rgy.format_if_db import FormatDescDb, FormatIfDb
from ucis.ucis import UCIS

def merge(args):
    if args.input_format is None:
        args.input_format = "xml"
    if args.output_format is None:
        args.output_format = "xml"

    rgy = FormatRgy.inst()
    if not rgy.hasDatabaseFormat(args.input_format):
        raise Exception("Input format %s not recognized" % args.input_format)
    if not rgy.hasDatabaseFormat(args.output_format):
        raise Exception("Output format %s not recognized" % args.output_format)

    # Build list of databases to merge
    db_files = list(args.db) if args.db else []
    
    # Read from file list if provided
    if args.file_list:
        import os
        if not os.path.exists(args.file_list):
            raise Exception("File list not found: %s" % args.file_list)
        
        with open(args.file_list, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and blank lines
                if line and not line.startswith('#'):
                    db_files.append(line)
    
    # Validate we have at least one database
    if len(db_files) == 0:
        raise Exception("No input databases specified. Use --file-list or provide database arguments.")

    input_desc : FormatDescDb = rgy.getDatabaseDesc(args.input_format)
    output_desc : FormatDescDb = rgy.getDatabaseDesc(args.output_format)

    out_if = output_desc.fmt_if()
    out_db : UCIS = out_if.create()
    db_if : FormatIfDb = input_desc.fmt_if()
    merger = DbMerger()

    for input in db_files:
        print("read and merge: ", input)
        out_db_ref : UCIS = out_if.create()
        db_l : List[UCIS] = []
        try:
            db = db_if.read(input)
            db_l.append(db)
            db_l.append(out_db)
        except Exception as e:
            raise Exception("Failed to read input file %s: %s" % (
                input,
                str(e)
            ))

        try:
            merger.merge(out_db_ref, db_l)
        except Exception as e:
            raise Exception("Merge operation failed: %s" % str(e))

        out_db = out_db_ref
        db.close()
    
    out_db.write(args.out)

    

'''
Created on Mar 24, 2020

@author: ballance
'''
import logging
import argparse
from ucis.ucis import UCIS
import os

def read_db(filename) -> UCIS:
    ext = os.path.splitext(filename)[1]
    
    if ext == "xml":
        logging.info("XML")
    elif ext == "scdb":
        logging.info("SCDB")
    else:
        raise Exception("Unknown file extension")
    
    return None

def report_cmd(args):
    db = read_db(args.db)
    
    pass

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", "-v",
        help="Enable verbose output")
    subparser = parser.add_subparsers()
    subparser.required = True
    
    report = subparser.add_parser("report",
        help="Produce a coverage report")
    report.add_argument("--text", "-t",
        help="Produce a coverage report in text format (default)")
    report.add_argument("--xml", "-x",
        help="Produce a coverage report in XML (Cobertura) format")
    report.add_argument("--output", "-o", 
        help="Specify the output name. Default is report.[ext]")
    report.add_argument("--detail", "-d",
        help="Include bin details in coverage report")
    report.add_argument("db",
        help="Database to read")
    report.set_defaults(func=report_cmd)
    
    return parser

def main():
    parser = get_parser()

    args = parser.parse_args()
    
    args.func(args)
    

if __name__ == "__main__":
    main()
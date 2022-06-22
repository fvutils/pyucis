'''
Created on Jun 11, 2022

@author: mballance
'''
import argparse
from . import cmd

def get_parser():
    parser = argparse.ArgumentParser()
    
    subparser = parser.add_subparsers()
    subparser.required = True
   
    merge = subparser.add_parser("merge")
    merge.add_argument("--out", "-o", 
        help="Specifies the output of the merge",
        required=True)
    merge.add_argument("--input-format", "-if",
        help="Specifies the format of the input databases. Defaults to 'xml'")
    merge.add_argument("--output-format", "-of",
        help="Specifies the format of the input databases. Defaults to 'xml'")
    merge.add_argument("--libucis", "-l",
        help="Specifies the name/path of the UCIS shared library")
    merge.add_argument("db", action="append")
    merge.set_defaults(func=cmd.cmd_merge.merge)
    
    return parser

def main():
    parser = get_parser()
    
    args = parser.parse()
    
    args.func(args)

if __name__ == "__main__":
    main()
    
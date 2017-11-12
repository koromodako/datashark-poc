#!/usr/bin/env python3

#===============================================================================
# IMPORTS
#===============================================================================
from utils.config          import config
from utils.config          import load_config
from utils.config          import print_license
from utils.config          import get_arg_parser
from utils.config          import print_license_warranty
from utils.config          import print_license_conditions
from dissection.dissector  import Dissector
from utils.helpers.logging import get_logger
from utils.helpers.logging import configure_logging
#===============================================================================
# GLOBALS
#===============================================================================
lgr = None
#===============================================================================
# FUNCTIONS 
#===============================================================================
def abort(msg, code):
    # TRACE
    exit(code)
#-------------------------------------------------------------------------------
# list_dissectors
#-------------------------------------------------------------------------------
def list_dissectors(args):
    lgr.debug('list_dissectors()')
    dissectors = Dissector.dissectors()
    lgr.info('dissectors:')
    if len(dissectors) > 0:
        for d in dissectors:
            lgr.info('\t+ {0}'.format(d))
    else:
        lgr.error('no dissector registered.')
#-------------------------------------------------------------------------------
# dissect
#-------------------------------------------------------------------------------
def dissect(args):
    lgr.debug('dissect()')
    d = Dissector()
    if len(args.files) > 0:
        for f in args.files:
            d.dissect(f)
    else:
        lgr.error('give at least one file to dissect.')
#-------------------------------------------------------------------------------
# ACTIONS
#-------------------------------------------------------------------------------
ACTIONS = {
    'list_dissectors': list_dissectors,
    'dissect': dissect 
}
#-------------------------------------------------------------------------------
# parse_args
#-------------------------------------------------------------------------------
def parse_args():
    parser = get_arg_parser()
    parser.add_argument('action', choices=list(ACTIONS.keys()), 
        help='Action to perform.')
    parser.add_argument('files', nargs='*', help='Files to process.')
    return parser.parse_args()
#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------
def main(args):
    global lgr
    lgr = get_logger(__name__)
    load_config(args.config)
    if args.warranty:
        print_license_warranty()
        return 0
    if args.conditions:
        print_license_conditions()
        return 0
    if not args.silent:
        print_license()
    ACTIONS[args.action](args)
    return 0
#===============================================================================
# SCIRPT
#===============================================================================
if __name__ == '__main__':
    args = parse_args()
    configure_logging(args.silent, args.verbose, args.debug)
    exit(main(args))
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
LGR = None
DISSECTOR = Dissector()
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
    LGR.debug('list_dissectors()')
    dissectors = DISSECTOR.dissectors()
    LGR.info('dissectors:')
    if len(dissectors) > 0:
        for mime in dissectors:
            LGR.info('\t+ {0}'.format(mime[0]))
            for dissector in mime[1]:
                LGR.info('\t\t+ {0}'.format(dissector))
    else:
        LGR.error('no dissector registered.')
#-------------------------------------------------------------------------------
# dissect
#-------------------------------------------------------------------------------
def dissect(args):
    LGR.debug('dissect()')
    if len(args.files) > 0:
        for f in args.files:
            DISSECTOR.dissect(f)
    else:
        LGR.error('give at least one file to dissect.')
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
def main():
    global LGR
    # parse input arguments
    args = parse_args()
    # print license if required
    if not args.silent:
        print_license()
    # configure logging module
    configure_logging(args.silent, args.verbose, args.debug)
    # retrieve module logger after logging module has been configured
    LGR = get_logger(__name__)
    # load datashark configuration
    load_config(args)
    # load dissectors
    DISSECTOR.load_dissectors()
    # process specific options
    if args.warranty:
        print_license_warranty()
        return 0
    if args.conditions:
        print_license_conditions()
        return 0
    # execute action
    ACTIONS[args.action](args)
    return 0
#===============================================================================
# SCIRPT
#===============================================================================
if __name__ == '__main__':
    exit(main())
#!/usr/bin/env python3

#===============================================================================
# IMPORTS
#===============================================================================
import os
from utils.config               import config
from utils.config               import load_config
from utils.config               import print_license
from utils.config               import get_arg_parser
from utils.config               import print_license_warranty
from utils.config               import print_license_conditions
from dissection.container       import ContainerActionGroup
from dissection.dissection      import DissectionActionGroup
from utils.helpers.logging      import get_logger
from utils.helpers.logging      import configure_logging
from utils.helpers.filtering    import FSEntryFilter
from dissection.hashdatabase    import HashDatabaseActionGroup
from utils.helpers.action_group import ActionGroup
#===============================================================================
# GLOBALS
#===============================================================================
LGR = None
DISSECTION_ACT_GRP = DissectionActionGroup()
HASHDB_ACT_GRP = HashDatabaseActionGroup()
CONTAINER_ACT_GRP = ContainerActionGroup()
ACTIONS = ActionGroup('datashark', {
    DISSECTION_ACT_GRP.name: DISSECTION_ACT_GRP,
    HASHDB_ACT_GRP.name: HASHDB_ACT_GRP,
    CONTAINER_ACT_GRP.name: CONTAINER_ACT_GRP
})
#===============================================================================
# FUNCTIONS 
#===============================================================================
#-------------------------------------------------------------------------------
# parse_args
#-------------------------------------------------------------------------------
def parse_args():
    parser = get_arg_parser()
    parser.add_argument('action', type=str, help='Action to perform.')
    parser.add_argument('-r', '--recursive', action='store_true', 
        help='Affects only hdb_create. Tells it to recurse inside given directories.')
    parser.add_argument('-n', '--num-workers', type=int, 
        help='Number of workers to be used to dissect containers.')
    parser.add_argument('-m', '--magic-file', type=str, default=None,
        help='Magic file to be used internally.')
    parser.add_argument('--include-dirs', type=str, default='',
        help='Comma-separated list of patterns.')
    parser.add_argument('--exclude-dirs', type=str, default='',
        help='Comma-separated list of patterns.')
    parser.add_argument('--include-files', type=str, default='',
        help='Comma-separated list of patterns.')
    parser.add_argument('--exclude-files', type=str, default='',
        help='Comma-separated list of patterns.')
    # optional processing
    parser.add_argument('--skip-failing-import', action='store_true', 
        help='Ignore dissectors that failed to be imported.')
    parser.add_argument('--skip-hash', action='store_true', 
        help='Do not hash containers. Warning: using this option prevents the use of white/blacklists.')
    parser.add_argument('files', nargs='*', help='Files to process.')
    return parser.parse_args()
#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------
def main():
    global LGR
    # parse input arguments
    args = parse_args()
    args.dir_filter = FSEntryFilter(args.include_dirs, args.exclude_dirs)
    args.file_filter = FSEntryFilter(args.include_files, args.exclude_files)
    # print license if required
    if not args.silent:
        print_license()
    # configure logging module
    configure_logging(args.silent, args.verbose, args.debug)
    # retrieve module logger after logging module has been configured
    LGR = get_logger(__name__)
    # load datashark configuration
    LGR.info('loading configuration...')
    load_config(args)
    LGR.info('configuration loaded.')
    # process specific options
    if args.warranty:
        print_license_warranty()
        return 0
    if args.conditions:
        print_license_conditions()
        return 0
    # execute action
    LGR.debug('running action: {0}'.format(args.action))
    ACTIONS.perform_action(args.action.split(ActionGroup.SEP), args)
    return 0
#===============================================================================
# SCIRPT
#===============================================================================
if __name__ == '__main__':
    exit(main())
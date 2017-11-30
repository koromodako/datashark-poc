#!/usr/bin/env python3

#===============================================================================
# IMPORTS
#===============================================================================
# modules imports
import os
import utils.helpers.logging        as logging
import utils.helpers.workspace      as workspace
# functions imports
from utils.config                   import config
from utils.config                   import load_config
from utils.config                   import print_license
from utils.config                   import print_version
from utils.config                   import get_arg_parser
from utils.config                   import print_license_warranty
from utils.config                   import print_license_conditions
from dissection.container           import ContainerActionGroup
from dissection.dissection          import DissectionActionGroup
from utils.helpers.logging          import get_logger
from utils.helpers.filtering        import FSEntryFilter
from dissection.hashdatabase        import HashDatabaseActionGroup
from utils.helpers.action_group     import ActionGroup
from dissection.dissectiondatabase  import DissectionDatabaseActionGroup
#===============================================================================
# GLOBALS
#===============================================================================
#
if not workspace.init():
    exit(101)
#
if not logging.init(workspace.workspace().logdir()):
    exit(102)
#
LGR = logging.get_logger(__name__)
HASHDB_ACT_GRP = HashDatabaseActionGroup()
CONTAINER_ACT_GRP = ContainerActionGroup()
DISSECTION_ACT_GRP = DissectionActionGroup()
DISSECTION_DB_ACT_GRP = DissectionDatabaseActionGroup()
WORKSPACE_ACT_GRP = workspace.action_group()
ACTIONS = ActionGroup('datashark', {
    HASHDB_ACT_GRP.name: HASHDB_ACT_GRP,
    WORKSPACE_ACT_GRP.name: WORKSPACE_ACT_GRP,
    CONTAINER_ACT_GRP.name: CONTAINER_ACT_GRP,
    DISSECTION_ACT_GRP.name: DISSECTION_ACT_GRP,
    DISSECTION_DB_ACT_GRP.name: DISSECTION_DB_ACT_GRP,
})
#===============================================================================
# FUNCTIONS 
#===============================================================================
#-------------------------------------------------------------------------------
# parse_args
#-------------------------------------------------------------------------------
def parse_args():
    LGR.debug('parse_args()')
    parser = get_arg_parser()
    # optional arguments
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
    # positional arguments
    parser.add_argument('action', nargs='?', type=str, help='Action to perform.')
    parser.add_argument('files', nargs='*', help='Files to process.')
    return parser.parse_args()
#-------------------------------------------------------------------------------
# handle_action
#-------------------------------------------------------------------------------
def handle_action(args):
    LGR.debug('handle_action()')
    # create FS entry filters
    args.dir_filter = FSEntryFilter(args.include_dirs, args.exclude_dirs)
    args.file_filter = FSEntryFilter(args.include_files, args.exclude_files)
    # load datashark configuration
    LGR.info('loading configuration...')
    conf = load_config(args)
    if conf is None:
        LGR.debug('no configuration file found.')
    else:
        LGR.debug('config loaded from: {}'.format(conf))
    LGR.info('configuration loaded.')
    # execute action
    LGR.debug('running action: {}'.format(args.action))
    ACTIONS.perform_action(args.action.split(ActionGroup.SEP), args)
    return 0
#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------
def main():
    LGR.debug('main()')
    # parse input arguments
    args = parse_args()
    # reconfigure logging module
    logging.reconfigure(args.silent, args.verbose, args.debug)
    LGR.debug('args: {}'.format(args))
    # process specific options
    if args.version:
        print_version()
        return 0
    if args.warranty:
        print_license_warranty()
        return 0
    if args.conditions:
        print_license_conditions()
        return 0
    # print license if required
    if not args.silent:
        print_license()
    return handle_action(args)
#===============================================================================
# SCIRPT
#===============================================================================
if __name__ == '__main__':
    code = main()
    workspace.term()
    exit(code)
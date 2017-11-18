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
from dissection.dissector       import Dissector
from utils.helpers.logging      import get_logger
from utils.helpers.logging      import configure_logging
from dissection.hashdatabase    import HashDatabase
#===============================================================================
# GLOBALS
#===============================================================================
LGR = None
#===============================================================================
# FUNCTIONS 
#===============================================================================
def abort(msg, code=42):
    LGR.error(msg)
    exit(code)
#-------------------------------------------------------------------------------
# list_dissectors
#-------------------------------------------------------------------------------
def list_dissectors(args):
    LGR.debug('list_dissectors()')
    dissectors = Dissector().dissectors()
    LGR.info('dissectors:')
    if len(dissectors) > 0:
        for mime in dissectors:
            LGR.info('\t+ {0}'.format(mime[0]))
            for dissector in mime[1]:
                LGR.info('\t\t+ {0}'.format(dissector))
    else:
        abort('no dissector registered.')
#-------------------------------------------------------------------------------
# dissect
#-------------------------------------------------------------------------------
def dissect(args):
    LGR.debug('dissect()')
    dissector = Dissector()
    dissector.load_hashdatabases()
    dissector.load_dissectors()
    if len(args.files) > 0:
        for f in args.files:
            dissector.dissect(f)
    else:
        abort('give at least one file to dissect.')
#-------------------------------------------------------------------------------
# hdb_create
#-------------------------------------------------------------------------------
def hdb_create(args):
    # check arguments
    if len(args.files) < 2:
        abort('missing arguments, hdb_create expects args: output.json dir [dir ...]')
    fpath = args.files[0]
    dirs = args.files[1:]
    if os.path.isdir(fpath):
        abort('<{0}> is an existing directory.'.format(fpath))
    for dpath in dirs:
        if not os.path.isdir(dpath):
            abort('<{0}> must be an existing directory.'.format(dpath))
    # create database
    HashDatabase.create(fpath, dirs, args.recursive)
#-------------------------------------------------------------------------------
# hdb_merge
#-------------------------------------------------------------------------------
def hdb_merge(args):
    # check arguments
    if len(args.files) < 2:
        abort('missing arguments, hdb_merge expects args: output.json db.part1.json db.part2.json ... db.partN.json')
    fpath = args.files[0]
    files = args.files[1:]
    if os.path.isdir(fpath):
        abort('<{0}> is an existing directory.'.format(fpath))
    for f in files:
        if not os.path.isfile(f):
            abort('<{0}> must be an existing file.'.format(f))
    # merge db files
    HashDatabase.merge(fpath, files)
#-------------------------------------------------------------------------------
# ACTIONS
#-------------------------------------------------------------------------------
ACTIONS = {
    'list_dissectors': list_dissectors,
    'dissect': dissect,
    'hdb_create': hdb_create,
    'hdb_merge': hdb_merge
}
#-------------------------------------------------------------------------------
# parse_args
#-------------------------------------------------------------------------------
def parse_args():
    parser = get_arg_parser()
    parser.add_argument('action', choices=list(ACTIONS.keys()), 
        help='Action to perform.')
    parser.add_argument('-r', '--recursive', action='store_true', 
        help='Affects only hdb_create. Tells it to recurse inside given directories.')
    parser.add_argument('-n', '--num-workers', type=int, 
        help='Number of workers to be used to dissect containers.')
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
    LGR.info('running action: {0}'.format(args.action))
    ACTIONS[args.action](args)
    return 0
#===============================================================================
# SCIRPT
#===============================================================================
if __name__ == '__main__':
    exit(main())
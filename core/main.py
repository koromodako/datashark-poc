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
from dissection.container       import Container
from dissection.dissector       import Dissector
from utils.helpers.logging      import get_logger
from utils.helpers.logging      import configure_logging
from utils.helpers.filtering    import FSEntryFilter
from dissection.hashdatabase    import HashDatabase
#===============================================================================
# GLOBALS
#===============================================================================
LGR = None
#===============================================================================
# FUNCTIONS 
#===============================================================================
#-------------------------------------------------------------------------------
# abort
#-------------------------------------------------------------------------------
def abort(msg, code=42):
    LGR.error(msg)
    exit(code)
#-------------------------------------------------------------------------------
# dissector_list
#-------------------------------------------------------------------------------
def dissector_list(args):
    LGR.debug('list_dissectors()')
    dissector = Dissector()
    dissector.load_dissectors()
    dissectors = dissector.dissectors()
    LGR.info('dissectors:')
    if len(dissectors) > 0:
        for mime in dissectors:
            LGR.info('\t+ {0}'.format(mime[0]))
            for dissector in mime[1]:
                LGR.info('\t\t+ {0}'.format(dissector))
    else:
        abort('no dissector registered.')
#-------------------------------------------------------------------------------
# dissector_dissect
#-------------------------------------------------------------------------------
def dissector_dissect(args):
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
    HashDatabase.create(fpath, dirs, args.recursive, 
        args.dir_filter, args.file_filter)
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
# container_hash
#-------------------------------------------------------------------------------
def container_hash(args):
    for f in args.files:
        if os.path.isfile(f):
            LGR.info('{0}: {1}'.format(f, Container.hash(f)))
        else:
            LGR.error('{0}: invalid path.')
#-------------------------------------------------------------------------------
# container_mimes
#-------------------------------------------------------------------------------
def container_mimes(args):
    for f in args.files:
        if os.path.isfile(f):
            mimes = Container.mimes(config('magic_file'), f)
            LGR.info('{0}:\n\tmime: {1}\n\ttext: {2}'.format(f, mimes[1], mimes[0]))
        else:
            LGR.error('{0}: invalid path.')
#===============================================================================
# ACTIONS
#===============================================================================
ACTIONS = {
    'dissector.list': dissector_list,
    'dissector.dissect': dissector_dissect,
    'hdb.create': hdb_create,
    'hdb.merge': hdb_merge,
    'container.hash': container_hash,
    'container.mimes': container_mimes
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
    ACTIONS[args.action](args)
    return 0
#===============================================================================
# SCIRPT
#===============================================================================
if __name__ == '__main__':
    exit(main())
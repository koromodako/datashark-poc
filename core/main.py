#!/usr/bin/env python3
# -!- encoding:utf8 -!-
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: main.py
#     date: 2017-12-02
#   author: paul.dautry
#  purpose:
#
#  license:
#    Datashark <progdesc>
#    Copyright (C) 2017 paul.dautry
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# =============================================================================
# IMPORTS
# =============================================================================
# modules imports
import os
import utils.logging as logging
import workspace.workspace as workspace
import utils.config as config
# functions imports
from utils.config import print_license
from utils.config import print_version
from utils.config import get_arg_parser
from utils.config import print_license_warranty
from utils.config import print_license_conditions
from utils.logging import get_logger
from utils.wrapper import trace_func
from hashdb.hashdb import HashDBActionGroup
from utils.filtering import FSEntryFilter
from utils.action_group import ActionGroup
from container.container import ContainerActionGroup
from dissection.dissection import DissectionActionGroup
from dissectiondb.dissectiondb import DissectionDBActionGroup
# =============================================================================
# GLOBALS
# =============================================================================
#
if not workspace.init():
    print("FATAL: failed to initialize workspace.")
    exit(100)
#
if not logging.init(workspace.workspace().logdir()):
    print("FATAL: failed to initialize logger.")
    exit(101)
#
LGR = logging.get_logger(__name__)
#
if not config.load():
    print("FATAL: failed to load config from file.")
    exit(102)
#
HASHDB_ACT_GRP = HashDBActionGroup()
CONTAINER_ACT_GRP = ContainerActionGroup()
DISSECTION_ACT_GRP = DissectionActionGroup()
DISSECTION_DB_ACT_GRP = DissectionDBActionGroup()
WORKSPACE_ACT_GRP = workspace.action_group()
ACTIONS = ActionGroup('datashark', {
    HASHDB_ACT_GRP.name: HASHDB_ACT_GRP,
    WORKSPACE_ACT_GRP.name: WORKSPACE_ACT_GRP,
    CONTAINER_ACT_GRP.name: CONTAINER_ACT_GRP,
    DISSECTION_ACT_GRP.name: DISSECTION_ACT_GRP,
    DISSECTION_DB_ACT_GRP.name: DISSECTION_DB_ACT_GRP,
})
# =============================================================================
# FUNCTIONS
# =============================================================================


@trace_func(__name__)
def parse_args():
    # -------------------------------------------------------------------------
    # parse_args
    # -------------------------------------------------------------------------
    parser = get_arg_parser()
    # optional arguments
    parser.add_argument('-r', '--recursive', action='store_true',
                        help="Affects only <hashdb.create> action."
                        "Tells it to recurse inside given directories.")

    parser.add_argument('-n', '--num-workers', type=int,
                        help="Number of workers to be used to dissect "
                        "containers.")

    parser.add_argument('-m', '--magic-file', type=str,
                        help="Magic file to be used internally.")

    parser.add_argument('--whitelist-config', type=str,
                        help="Specify a different whitelist db configuration "
                        "file.")
    parser.add_argument('--blacklist-config', type=str,
                        help="Specify a different blacklist db configuration "
                        "file.")
    parser.add_argument('--dissection-config', type=str,
                        help="Specify a different dissection configuration "
                        "file.")

    parser.add_argument('--include-dirs', type=str,
                        help="Comma-separated list of patterns.")
    parser.add_argument('--exclude-dirs', type=str,
                        help="Comma-separated list of patterns.")
    parser.add_argument('--include-files', type=str,
                        help="Comma-separated list of patterns.")
    parser.add_argument('--exclude-files', type=str,
                        help="Comma-separated list of patterns.")

    # optional processing
    parser.add_argument('--cleanup',
                        action='store_true',
                        help="Cleanup workspace after processing.")
    parser.add_argument('--skip-failing-import',
                        action='store_true',
                        help="Ignore dissectors that failed to be imported.")
    parser.add_argument('--skip-hash',
                        action='store_true',
                        help="Do not hash containers. Warning: using this "
                        "option prevents the use of white/blacklists.")

    # positional arguments
    parser.add_argument('action',
                        nargs='?',
                        type=str,
                        default=None,
                        help="Action to perform.")
    parser.add_argument('files',
                        nargs='*',
                        help="Files to process.")

    return parser.parse_args()


@trace_func(__name__)
def handle_action(args):
    # -------------------------------------------------------------------------
    # handle_action
    # -------------------------------------------------------------------------
    config.set_args(args)
    # create FS entry filters
    args.dir_filter = FSEntryFilter(config.value('include_dirs'),
                                    config.value('exclude_dirs'))
    args.file_filter = FSEntryFilter(config.value('include_files'),
                                     config.value('exclude_files'))
    # execute action
    LGR.debug('running action: {}'.format(args.action))
    if args.action is None:
        LGR.error("get started with: `datashark help` ;)")
        return 1

    if not ACTIONS.perform_action(args.action.split(ActionGroup.SEP), args):
        return 2
    return 0


@trace_func(__name__)
def main():
    # -------------------------------------------------------------------------
    # main
    # -------------------------------------------------------------------------
    # parse input arguments
    args = parse_args()

    logging.reconfigure(args.silent, args.verbose, args.debug)
    LGR.debug('args: {}'.format(args))

    if args.version:
        print_version()
        return 0

    if args.warranty:
        print_license_warranty()
        return 0

    if args.conditions:
        print_license_conditions()
        return 0

    if not args.silent:
        print_license()

    code = handle_action(args)

    if args.cleanup:
        workspace.cleanup()

    return code


# ==============================================================================
# SCIRPT
# ==============================================================================
if __name__ == '__main__':
    code = main()
    workspace.term()
    exit(code)

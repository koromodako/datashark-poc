#!/usr/bin/env python3
# -!- encoding:utf8 -!-
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: main.py
#     date: 2017-12-02
#   author: koromodako
#  purpose:
#
#  license:
#    Datashark <progdesc>
#    Copyright (C) 2017 koromodako
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
#
from utils.constants import check_python_version
if not check_python_version(3, 6, 0):
    print("FATAL: requires python version 3.6.x or newer.")
    exit(100)
#
import os
import functools
import utils.logging as logging
import workspace.workspace as workspace
import utils.config as config
#
from utils.config import print_license
from utils.config import print_version
from utils.config import get_arg_parser
from utils.config import print_license_warranty
from utils.config import print_license_conditions
from utils.logging import get_logger
from utils.wrapper import trace_func
from hashdb.hashdb import HashDBActionGroup
from utils.filtering import FSEntryFilter
from utils.converting import str2int
from utils.action_group import ActionGroup
from container.container import ContainerActionGroup
from workspace.workspace import WorkspaceActionGroup
from dissection.dissection import DissectionActionGroup
from dissectiondb.dissectiondb import DissectionDBActionGroup
# =============================================================================
# GLOBALS
# =============================================================================
#
if not workspace.init():
    print("FATAL: failed to initialize workspace.")
    exit(101)
#
if not logging.init(workspace.workspace().logdir()):
    print("FATAL: failed to initialize logger.")
    exit(102)
#
LGR = logging.get_logger(__name__)
#
if not config.load():
    print("FATAL: failed to load config from file.")
    exit(103)
#
HASHDB_ACT_GRP = HashDBActionGroup()
CONTAINER_ACT_GRP = ContainerActionGroup()
DISSECTION_ACT_GRP = DissectionActionGroup()
DISSECTION_DB_ACT_GRP = DissectionDBActionGroup()
WORKSPACE_ACT_GRP = WorkspaceActionGroup()
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
##
## @brief      { function_description }
##
## @return     { description_of_the_return_value }
##
@trace_func(__name__)
def parse_args():
    parser = get_arg_parser()
    # optional configuration
    parser.add_argument('-r', '--recursive', action='store_true',
                        help="Affects only <hashdb.create> action."
                        "Tells it to recurse inside given directories.")

    parser.add_argument('-n', '--num-workers', type=int,
                        help="Number of workers to be used to dissect "
                        "containers.")

    parser.add_argument('-m', '--magic-file',
                        help="Magic file to be used internally.")

    parser.add_argument('--whitelist-config',
                        help="Specify a different whitelist db configuration "
                        "file.")
    parser.add_argument('--blacklist-config',
                        help="Specify a different blacklist db configuration "
                        "file.")
    parser.add_argument('--dissection-config',
                        help="Specify a different dissection configuration "
                        "file.")

    parser.add_argument('--include-dirs',
                        help="Comma-separated list of patterns.")
    parser.add_argument('--exclude-dirs',
                        help="Comma-separated list of patterns.")
    parser.add_argument('--include-files',
                        help="Comma-separated list of patterns.")
    parser.add_argument('--exclude-files',
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

    # action-specific arguments
    parser.add_argument('--max-lines', type=int, default=20,
                        help="Max number of lines to display when "
                             "'hexdumping'. Set it to 0 for infinite.")
    parser.add_argument('-i', '--index', type=str2int,
                        help="An index: integer value as 0b, 0o, 0x or dec.")
    parser.add_argument('-o', '--offset', type=str2int,
                        help="An offset: integer value as 0b, 0o, 0x or dec.")
    parser.add_argument('-s', '--size', type=str2int,
                        help="A size: integer value as 0b, 0o, 0x or dec.")
    parser.add_argument('-p', '--path',
                        help="")

    # positional arguments
    parser.add_argument('action',
                        nargs='?',
                        default=None,
                        help="Action to perform.")
    parser.add_argument('files',
                        nargs='*',
                        help="Files to process.")

    return parser.parse_args()
##
## @brief      { function_description }
##
## @param      args  The arguments
##
## @return     { description_of_the_return_value }
##
@trace_func(__name__)
def handle_action(args):
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
##
## @brief      { function_description }
##
## @return     { description_of_the_return_value }
##
@trace_func(__name__)
def main():
    # parse input arguments
    args = parse_args()

    logging.reconfigure(args.quiet, args.verbose, args.debug)
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

    if not args.quiet:
        print_license()

    try:
        code = handle_action(args)
    except Exception as e:
        LGR.exception("unhandled internal exception.")
        LGR.critical("terminating gracefully.")
        code = 707

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

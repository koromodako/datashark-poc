# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: workspace.py
#    date: 2017-11-30
#  author: paul.dautry
# purpose:
#
# license:
#   Datashark <progdesc>
#   Copyright (C) 2017 paul.dautry
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# =============================================================================
# IMPORTS
# =============================================================================
#
import os
#
from shutil import rmtree
from utils.crypto import randstr
from utils.wrapper import trace
from utils.logging import get_logger
from utils.wrapper import trace_func
from utils.wrapper import trace_static
from utils.binary_file import BinaryFile
from utils.action_group import ActionGroup
# ==============================================================================
# GLOBALS
# ==============================================================================
WORKSPACE = None
LGR = get_logger(__name__)
# ==============================================================================
# CLASSES
# ==============================================================================
##
## @brief      Class for workspace.
##
class Workspace(object):
    ##
    ## { item_description }
    ##
    WS_ROOT_DIR = os.path.expanduser('~/datashark.ws')
    ##
    ## { item_description }
    ##
    WS_PREFIX = 'ds.ws.'
    ##
    ## @brief      Constructs the object.
    ##
    def __init__(self):
        randdir = '{}{}'.format(self.WS_PREFIX, randstr(4))
        self.__ws_root = os.path.join(self.WS_ROOT_DIR, randdir)
        self.__ws_logdir = os.path.join(self.__ws_root, 'logs')
        self.__ws_tmpdir = os.path.join(self.__ws_root, 'tmp')
        self.__ws_datdir = os.path.join(self.__ws_root, 'data')
    ##
    ## @brief      { function_description }
    ##
    ## @param      abspath  The abspath
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def __mkdir(self, abspath):
        os.makedirs(abspath, exist_ok=True)
        return abspath
    ##
    ## @brief      { function_description }
    ##
    ## @param      prefix     The prefix
    ## @param      suffix     The suffix
    ## @param      randomize  The randomize
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def __filename(self, prefix, suffix, randomize):
        parts = [prefix, randstr(4) if randomize else '', suffix]
        parts = list(filter(None, parts))
        return '.'.join(parts)
    ##
    ## @brief      { function_description }
    ##
    ## @param      absdir     The absdir
    ## @param      prefix     The prefix
    ## @param      suffix     The suffix
    ## @param      isdir      The isdir
    ## @param      randomize  The randomize
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def __file(self, absdir, prefix, suffix, isdir=False, randomize=True):
        # --------------------------------------------------------------------------
        # __file
        # --------------------------------------------------------------------------
        full_path = os.path.join(absdir, self.__filename(prefix, suffix,
                                                         randomize))
        if isdir:
            return self.__mkdir(full_path)

        return BinaryFile(full_path, 'w')
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def init(self):
        self.__mkdir(self.__ws_logdir)
        self.__mkdir(self.__ws_datdir)
        self.__mkdir(self.__ws_tmpdir)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def cleanup(self):
        if os.path.isdir(self.__ws_tmpdir):
            rmtree(self.__ws_tmpdir)  # remove temporary directory (cleanup)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def term(self):
        pass
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def logdir(self):
        return self.__ws_logdir
    ##
    ## @brief      { function_description }
    ##
    ## @param      name  The name
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def logfile(self, name):
        return self.__file(self.__ws_logdir, name, '', randomize=False)
    ##
    ## @brief      { function_description }
    ##
    ## @param      subdir  The subdir
    ## @param      prefix  The prefix
    ## @param      suffix  The suffix
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def datdir(self, subdir=False, prefix='', suffix=''):
        if subdir:
            return self.__file(self.__ws_datdir, prefix, suffix, isdir=True)

        return self.__ws_datdir
    ##
    ## @brief      { function_description }
    ##
    ## @param      prefix  The prefix
    ## @param      suffix  The suffix
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def datfile(self, prefix='', suffix=''):
        return self.__file(self.__ws_datdir, prefix, suffix)
    ##
    ## @brief      { function_description }
    ##
    ## @param      subdir  The subdir
    ## @param      prefix  The prefix
    ## @param      suffix  The suffix
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def tmpdir(self, subdir=False, prefix='', suffix=''):
        if subdir:
            return self.__file(self.__ws_tmpdir, prefix, suffix, isdir=True)

        return self.__ws_tmpdir
    ##
    ## @brief      { function_description }
    ##
    ## @param      prefix  The prefix
    ## @param      suffix  The suffix
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def tmpfile(self, prefix='', suffix=''):
        return self.__file(self.__ws_tmpdir, prefix, suffix)
    ##
    ## @brief      { function_description }
    ##
    ## @param      fp    { parameter_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def filepath(self, fp):
        return os.path.abspath(fp.name)
##
## @brief      Class for workspace action group.
##
class WorkspaceActionGroup(ActionGroup):
    ##
    ## @brief      { function_description }
    ##
    ## @param      keywords  The keywords
    ## @param      args      The arguments
    ##
    ## @return     { description_of_the_return_value }
    ##
    @staticmethod
    @trace_static('WorkspaceActionGroup')
    def list(keywords, args):
        total = 0

        text = '\nworkspaces:\n'
        for entry in os.listdir(Workspace.WS_ROOT_DIR):
            full_path = os.path.join(Workspace.WS_ROOT_DIR, entry)

            if os.path.isdir(full_path):
                if entry.startswith(Workspace.WS_PREFIX):
                    total += 1
                    text += '\t+ {}\n'.format(full_path)

        text += '\ntotal: {}\n'.format(total)
        LGR.info(text)

        return True
    ##
    ## @brief      { function_description }
    ##
    ## @param      keywords  The keywords
    ## @param      args      The arguments
    ##
    ## @return     { description_of_the_return_value }
    ##
    @staticmethod
    @trace_static('WorkspaceActionGroup')
    def clean(keywords, args):
        only = args.files

        for entry in os.listdir(Workspace.WS_ROOT_DIR):

            if len(only) > 0 and entry not in only:
                continue

            full_path = os.path.join(Workspace.WS_ROOT_DIR, entry)

            if os.path.isdir(full_path):
                if entry.startswith(Workspace.WS_PREFIX):
                    LGR.info('removing {}...'.format(full_path))
                    rmtree(full_path)

        return True
    ##
    ## @brief      Constructs the object.
    ##
    def __init__(self):
        super(WorkspaceActionGroup, self).__init__('workspace', {
            'list': ActionGroup.action(WorkspaceActionGroup.list,
                                       "lists workspaces."),
            'clean': ActionGroup.action(WorkspaceActionGroup.clean,
                                        "removes all workspaces.")
        })
# ==============================================================================
# FUNCTIONS
# ==============================================================================
##
## @brief      { function_description }
##
## @return     { description_of_the_return_value }
##
@trace_func(__name__)
def init():
    global WORKSPACE

    if WORKSPACE is None:
        WORKSPACE = Workspace()

        try:
            WORKSPACE.init()
            return True
        except Exception as e:
            print(e)

    return False
##
## @brief      { function_description }
##
## @return     { description_of_the_return_value }
##
@trace_func(__name__)
def cleanup():
    if WORKSPACE is not None:
        WORKSPACE.cleanup()
        return True

    return False
##
## @brief      { function_description }
##
## @return     { description_of_the_return_value }
##
@trace_func(__name__)
def term():
    if WORKSPACE is not None:
        WORKSPACE.term()
        return True

    return False
##
## @brief      { function_description }
##
## @return     { description_of_the_return_value }
##
@trace_func(__name__)
def workspace():
    return WORKSPACE

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
from tempfile import gettempdir
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


class Workspace(object):
    # ------------------------------------------------------------------------------
    # Workspace
    # ------------------------------------------------------------------------------
    WS_PREFIX = 'ds.ws.'

    def __init__(self):
        # --------------------------------------------------------------------------
        # __init__
        # --------------------------------------------------------------------------
        randdir = '{}{}'.format(self.WS_PREFIX, randstr(4))
        self.__ws_root = os.path.join(gettempdir(), randdir)
        self.__ws_logdir = os.path.join(self.__ws_root, 'logs')
        self.__ws_tmpdir = os.path.join(self.__ws_root, 'tmp')
        self.__ws_datdir = os.path.join(self.__ws_root, 'data')

    @trace(LGR)
    def __mkdir(self, abspath):
        # --------------------------------------------------------------------------
        # __mkdir
        # --------------------------------------------------------------------------
        os.makedirs(abspath, exist_ok=True)
        return abspath

    @trace(LGR)
    def __filename(self, prefix, suffix, randomize):
        # --------------------------------------------------------------------------
        # __filename
        # --------------------------------------------------------------------------
        parts = [prefix, randstr(4) if randomize else '', suffix]
        parts = list(filter(None, parts))
        return '.'.join(parts)

    @trace(LGR)
    def __file(self, absdir, prefix, suffix, isdir=False, randomize=True):
        # --------------------------------------------------------------------------
        # __file
        # --------------------------------------------------------------------------
        full_path = os.path.join(absdir, self.__filename(prefix, suffix,
                                                         randomize))
        if isdir:
            return self.__mkdir(full_path)

        return BinaryFile(full_path, 'w')

    @trace(LGR)
    def init(self):
        # --------------------------------------------------------------------------
        # init
        # --------------------------------------------------------------------------
        self.__mkdir(self.__ws_logdir)
        self.__mkdir(self.__ws_datdir)
        self.__mkdir(self.__ws_tmpdir)

    @trace(LGR)
    def cleanup(self):
        # --------------------------------------------------------------------------
        # cleanup
        # --------------------------------------------------------------------------
        if os.path.isdir(self.__ws_tmpdir):
            rmtree(self.__ws_tmpdir)  # remove temporary directory (cleanup)

    @trace(LGR)
    def term(self):
        # --------------------------------------------------------------------------
        # term
        # --------------------------------------------------------------------------
        pass

    @trace(LGR)
    def logdir(self):
        # --------------------------------------------------------------------------
        # logdir
        # --------------------------------------------------------------------------
        return self.__ws_logdir

    @trace(LGR)
    def logfile(self, name):
        # --------------------------------------------------------------------------
        # logfile
        # --------------------------------------------------------------------------
        return self.__file(self.__ws_logdir, name, '', randomize=False)

    @trace(LGR)
    def datdir(self, subdir=False, prefix='', suffix=''):
        # --------------------------------------------------------------------------
        # datdir
        # --------------------------------------------------------------------------
        if subdir:
            return self.__file(self.__ws_datdir, prefix, suffix, isdir=True)

        return self.__ws_datdir

    @trace(LGR)
    def datfile(self, prefix='', suffix=''):
        # --------------------------------------------------------------------------
        # datfile
        # --------------------------------------------------------------------------
        return self.__file(self.__ws_datdir, prefix, suffix)

    @trace(LGR)
    def tmpdir(self, subdir=False, prefix='', suffix=''):
        # --------------------------------------------------------------------------
        # tmpdir
        # --------------------------------------------------------------------------
        if subdir:
            return self.__file(self.__ws_tmpdir, prefix, suffix, isdir=True)

        return self.__ws_tmpdir

    @trace(LGR)
    def tmpfile(self, prefix='', suffix=''):
        # --------------------------------------------------------------------------
        # tmpfile
        # --------------------------------------------------------------------------
        return self.__file(self.__ws_tmpdir, prefix, suffix)

    @trace(LGR)
    def filepath(self, fp):
        # ---------------------------------------------------------------------
        # filepath
        # ---------------------------------------------------------------------
        return os.path.abspath(fp.name)
# ==============================================================================
# FUNCTIONS
# ==============================================================================

@trace_func(LGR)
def init():
    # ------------------------------------------------------------------------------
    # init
    # ------------------------------------------------------------------------------
    global WORKSPACE

    if WORKSPACE is None:
        WORKSPACE = Workspace()

        try:
            WORKSPACE.init()
            return True
        except Exception as e:
            print(e)

    return False

@trace_func(LGR)
def cleanup():
    # -------------------------------------------------------------------------
    # cleanup
    # -------------------------------------------------------------------------
    if WORKSPACE is not None:
        WORKSPACE.cleanup()
        return True

    return False

@trace_func(LGR)
def term():
    # ------------------------------------------------------------------------------
    # term
    # ------------------------------------------------------------------------------
    if WORKSPACE is not None:
        WORKSPACE.term()
        return True

    return False

@trace_func(LGR)
def workspace():
    # ------------------------------------------------------------------------------
    # workspace
    # ------------------------------------------------------------------------------
    return WORKSPACE

@trace_func(LGR)
def action_group():
    # ------------------------------------------------------------------------------
    # action_group
    # ------------------------------------------------------------------------------
    @trace_func(LGR)
    def __action_list(keywords, args):
        # --------------------------------------------------------------------------
        # __action_list
        # --------------------------------------------------------------------------
        total = 0
        tmpdir = gettempdir()

        text = '\nworkspaces:\n'
        for entry in os.listdir(tmpdir):
            full_path = os.path.join(tmpdir, entry)

            if os.path.isdir(full_path):
                if entry.startswith(Workspace.WS_PREFIX):
                    total += 1
                    text += '\t+ {}\n'.format(full_path)

        text += '\ntotal: {}\n'.format(total)
        LGR.info(text)

    @trace_func(LGR)
    def __action_clean(keywords, args):
        # --------------------------------------------------------------------------
        # __action_clean
        # --------------------------------------------------------------------------
        tmpdir = gettempdir()

        only = args.files

        for entry in os.listdir(tmpdir):

            if len(only) > 0 and entry not in only:
                continue

            full_path = os.path.join(tmpdir, entry)

            if os.path.isdir(full_path):
                if entry.startswith(Workspace.WS_PREFIX):
                    LGR.info('removing {}...'.format(full_path))
                    rmtree(full_path)
    # -------------------------------------------------------------------------
    # ActionGroup
    # -------------------------------------------------------------------------
    return ActionGroup('workspace', {
        'list': ActionGroup.action(__action_list, 'lists workspaces.'),
        'clean': ActionGroup.action(__action_clean, 'removes all workspaces.')
    })

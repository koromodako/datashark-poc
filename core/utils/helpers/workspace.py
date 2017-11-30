#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#===============================================================================
# IMPORTS
#===============================================================================
#
import os
#
from shutil                     import rmtree
from tempfile                   import gettempdir
from utils.helpers.crypto       import randstr
from utils.helpers.action_group import ActionGroup
#===============================================================================
# GLOBALS
#===============================================================================
WORKSPACE = None
#===============================================================================
# CLASSES
#===============================================================================
#-------------------------------------------------------------------------------
# Workspace
#-------------------------------------------------------------------------------
class Workspace(object):
    WS_PREFIX = 'ds.ws.'
    #---------------------------------------------------------------------------
    # action_clean
    #---------------------------------------------------------------------------
    @staticmethod
    def action_clean(keywords, args):
        tmpdir = gettempdir()
        for entry in os.listdir(tmpdir):
            full_path = os.path.join(tmpdir, entry)
            if os.path.isdir(full_path) and entry.startswith(Workspace.WS_PREFIX):
                rmtree(full_path)
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self):
        randdir = '{}{}'.format(self.WS_PREFIX, randstr(4))
        self.__ws_root = os.path.join(gettempdir(), randdir)
        self.__ws_logdir = os.path.join(self.__ws_root, 'logs')
        self.__ws_tmpdir = os.path.join(self.__ws_root, 'tmp')
        self.__ws_datdir = os.path.join(self.__ws_root, 'data')
    #---------------------------------------------------------------------------
    # __mkdir
    #---------------------------------------------------------------------------
    def __mkdir(self, abspath):
        os.makedirs(abspath, exist_ok=True)
        return abspath
    #---------------------------------------------------------------------------
    # __filename
    #---------------------------------------------------------------------------
    def __filename(self, prefix, suffix, randomize):
        return '{}.{}.{}'.format(prefix, randstr(4) if randomize else '', suffix)
    #---------------------------------------------------------------------------
    # __file
    #---------------------------------------------------------------------------
    def __file(self, absdir, prefix, suffix, isdir=False, randomize=True):
        full_path = os.path.join(absdir, self.__filename(prefix, suffix, randomize))
        if isdir:
            return self.__mkdir(full_path)
        else:
            return open(full_path, 'w')
    #---------------------------------------------------------------------------
    # init
    #---------------------------------------------------------------------------
    def init(self):
        self.__mkdir(self.__ws_logdir)
        self.__mkdir(self.__ws_datdir)
        self.__mkdir(self.__ws_tmpdir)
    #---------------------------------------------------------------------------
    # term
    #---------------------------------------------------------------------------
    def term(self):
        if os.path.isdir(self.__ws_tmpdir):
            rmtree(self.__ws_tmpdir) # remove temporary directory (cleanup)
    #---------------------------------------------------------------------------
    # logdir
    #---------------------------------------------------------------------------
    def logdir(self):
        return self.__ws_logdir
    #---------------------------------------------------------------------------
    # logfile
    #---------------------------------------------------------------------------
    def logfile(self, name):
        return self.__file(self.__ws_logdir, name, '', randomize=False)
    #---------------------------------------------------------------------------
    # datdir
    #---------------------------------------------------------------------------
    def datdir(self, subdir=False, prefix='', suffix=''):
        if subdir:
            return self.__file(self.__ws_datdir, prefix, suffix, isdir=True)
        return self.__ws_datdir
    #---------------------------------------------------------------------------
    # datfile
    #---------------------------------------------------------------------------
    def datfile(self, prefix='', suffix=''):
        return self.__file(self.__ws_datdir, prefix, suffix)
    #---------------------------------------------------------------------------
    # tmpdir
    #---------------------------------------------------------------------------
    def tmpdir(self, subdir=False, prefix='', suffix=''):
        if subdir:
            return self.__file(self.__ws_tmpdir, prefix, suffix, isdir=True)
        return self.__ws_tmpdir
    #---------------------------------------------------------------------------
    # tmpfile
    #---------------------------------------------------------------------------
    def tmpfile(self, prefix='', suffix=''):
        return self.__file(self.__ws_tmpdir, prefix, suffix)
#===============================================================================
# FUNCTIONS
#===============================================================================
#-------------------------------------------------------------------------------
# init
#-------------------------------------------------------------------------------
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
#-------------------------------------------------------------------------------
# term
#-------------------------------------------------------------------------------
def term():
    if WORKSPACE is not None:
        WORKSPACE.term()
        return True
    return False
#-------------------------------------------------------------------------------
# workspace
#-------------------------------------------------------------------------------
def workspace():
    return WORKSPACE
#-------------------------------------------------------------------------------
# action_group
#-------------------------------------------------------------------------------
def action_group():
    return ActionGroup('workspace', {
        'clean': ActionGroup.action(Workspace.action_clean, 
            'removes all workspaces from <{}> directory.'.format(gettempdir()))
    })
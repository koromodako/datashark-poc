#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: json_adapter.py
#    date: 2017-11-28
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
import json
#
from utils.helpers.logging      import todo
from utils.helpers.logging      import get_logger
from utils.helpers.workspace    import workspace
#===============================================================================
# GLOBALS / CONFIG
#===============================================================================
LGR = get_logger(__name__)
JSON_FILE = None
BEGIN = '{"containers":['
END = ']}'
#===============================================================================
# CLASSES
#===============================================================================
#-------------------------------------------------------------------------------
# JsonFile
#-------------------------------------------------------------------------------
class JsonFile(object):
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self, name):
        super(JsonFile, self).__init__()
        self.name = name
        self.__sz = 0
        self.__fp = None
    #---------------------------------------------------------------------------
    # open
    #---------------------------------------------------------------------------
    def open(self):
        self.__sz = 0
        self.__fp = workspace().datfile(self.name, 'json')
    #---------------------------------------------------------------------------
    # close
    #---------------------------------------------------------------------------
    def close(self):
        self.__sz = 0
        self.__fp.close()
        self.__fp = None
    #---------------------------------------------------------------------------
    # write
    #---------------------------------------------------------------------------
    def write(self, data):
        self.__sz += len(data)
        self.__fp.write(data)
    #---------------------------------------------------------------------------
    # seek
    #---------------------------------------------------------------------------
    def seek(self, offset):
        self.__fp.seek(offset)
    #---------------------------------------------------------------------------
    # size
    #---------------------------------------------------------------------------
    def size(self):
        return self.__sz
#===============================================================================
# FUNCTIONS
#===============================================================================
#-------------------------------------------------------------------------------
# __container_to_json
#-------------------------------------------------------------------------------
def __container_to_json(container):
    return json.dumps(container.to_dict(), separators=(':',','))
#-------------------------------------------------------------------------------
# init
#-------------------------------------------------------------------------------
def init(config):
    global JSON_FILE
    LGR.debug('init()')
    JSON_FILE = JsonFile(config.get('filename', 'db'))
    JSON_FILE.open()
    JSON_FILE.write(BEGIN)
    return True
#-------------------------------------------------------------------------------
# term
#-------------------------------------------------------------------------------
def term():
    LGR.debug('term()')
    sz = JSON_FILE.size()
    if sz > len(BEGIN):
        JSON_FILE.seek(sz-2)
    JSON_FILE.write(END)
    JSON_FILE.close()
#-------------------------------------------------------------------------------
# persist
#-------------------------------------------------------------------------------
def persist(container):
    LGR.debug('persist()')
    json = __container_to_json(container)
    json += ','
    JSON_FILE.write(json)
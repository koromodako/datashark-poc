#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: octet_stream_dissector.py
#    date: 2017-11-11
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
from utils.helpers.cli          import CLI
from utils.helpers.logging      import get_logger
from model.objects.container    import Container 
#===============================================================================
# GLOBAL
#===============================================================================
#===============================================================================
# GLOBALS / CONFIG
#===============================================================================
lgr = get_logger(__name__)
QEMU_IMG = 'qemu-img'
#===============================================================================
# FUNCTIONS
#===============================================================================
#-------------------------------------------------------------------------------
# mimes
#   /!\ public mandatory function that the module must define /!\
#   \brief returns a list of mime types that this dissector can handle
#   \return [list(str)]
#-------------------------------------------------------------------------------
def mimes():
    lgr.debug('mimes()')
    return [
        'application/octet-stream'
    ]
#-------------------------------------------------------------------------------
# can_dissect
#   /!\ public mandatory function that the module must define /!\
#   \brief returns true if dissector can effectively dissect given container
#   \param [Container] container 
#   \return [bool]
#-------------------------------------------------------------------------------
def can_dissect(container):
    lgr.debug('can_dissect()')
    return CLI.look_for_commands([
        QEMU_IMG
    ])
#-------------------------------------------------------------------------------
# dissect
#   /!\ public mandatory function that the module must define /!\
#   \brief realize the dissection of the container and returns a list of 
#          containers found in the dissected container
#   \return [list(Container)]
#-------------------------------------------------------------------------------
def dissect(container):
    lgr.debug('dissect()')
    #return []
    raise NotImplementedError
#===============================================================================
# CLASSES
#===============================================================================
#===============================================================================
# SCRIPT
#===============================================================================
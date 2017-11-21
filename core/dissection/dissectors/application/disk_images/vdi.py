#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: vdi.py
#    date: 2017-11-18
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
from dissection.container       import Container
from dissection.structure       import StructSpecif
from dissection.structure       import StructFactory
from utils.helpers.logging      import get_logger
from utils.helpers.action_group import ActionGroup
#===============================================================================
# GLOBALS / CONFIG
#===============================================================================
LGR = get_logger(__name__)
StructFactory.register_structure(StructSpecif('VDIHeader', [
    StructSpecif.member('magic', 'ba:0x40'),
    StructSpecif.member('signature', 'ba:0x04'),
    StructSpecif.member('vmajor', '<H'),
    StructSpecif.member('vminor', '<H'),
    StructSpecif.member('hdr_sz', '<I'),
    StructSpecif.member('img_type', '<I'),
    StructSpecif.member('img_flags', '<I'),
    StructSpecif.member('img_desc', 'ba:0x100'),
    StructSpecif.member('oft_blk', '<I'),
    StructSpecif.member('oft_dat', '<I'),
    StructSpecif.member('num_cylinders', '<I'),
    StructSpecif.member('num_heads', '<I'),
    StructSpecif.member('num_sectors', '<I'),
    StructSpecif.member('sector_sz', '<I'),
    StructSpecif.member('pad0','<I'),
    StructSpecif.member('disk_sz', '<Q'),
    StructSpecif.member('blk_sz', '<I'),
    StructSpecif.member('blk_extra_dat', '<I'),
    StructSpecif.member('num_blk_in_hdd', '<I'),
    StructSpecif.member('num_blk_allocated', '<I'),
    StructSpecif.member('uuid_vdi', 'ba:0x10'),
    StructSpecif.member('uuid_last_snap', 'ba:0x10'),
    StructSpecif.member('uuid_link', 'ba:0x10'),
    StructSpecif.member('uuid_parent', 'ba:0x10'),
    StructSpecif.member('pad1', 'ba:0x38')
]))
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
    LGR.debug('mimes()')
    return [
        'application/octet-stream'
    ]
#-------------------------------------------------------------------------------
# configure
#   /!\ public mandatory function that the module must define /!\
#   \brief configures the dissector internal parameters
#   \param [list(tuple(option, value))] config
#       configuration taken from Datashark's INI file if found.
#       config might be None or empty.
#-------------------------------------------------------------------------------
def configure(config):
    LGR.debug('configure()')
    return True
#-------------------------------------------------------------------------------
# can_dissect
#   /!\ public mandatory function that the module must define /!\
#   \brief returns true if dissector can effectively dissect given container
#   \param [Container] container 
#   \return [bool]
#-------------------------------------------------------------------------------
def can_dissect(container):
    LGR.debug('can_dissect()')
    return ('VirtualBox Disk Image' in container.mime_text)
#-------------------------------------------------------------------------------
# dissect
#   /!\ public mandatory function that the module must define /!\
#   \brief realize the dissection of the container and returns a list of 
#          containers found in the dissected container
#   \param 
#   \return [list(Container)]
#-------------------------------------------------------------------------------
def dissect(container):
    LGR.debug('dissect()')
    with open(container.path, 'rb') as f:
        vdi_header = StructFactory.obj_from_file('VDIHeader', f)
        LGR.info(StructFactory.obj_to_str(vdi_header))
    # TODO : implement raw disk extraction
    raise NotImplementedError
    return []
#-------------------------------------------------------------------------------
# action_group()
#   /!\ public mandatory function that the module must define /!\
#   \brief returns module action group
#-------------------------------------------------------------------------------
def action_group():
    return ActionGroup('vdi', {})
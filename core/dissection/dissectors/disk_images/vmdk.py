#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: vmdk.py
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
StructFactory.register_structure(StructSpecif('SparseExtentHeader', [
    StructSpecif.member('magicNumber', 'ba:4'),
    StructSpecif.member('version', '<I'),
    StructSpecif.member('flags', '<I'),
    StructSpecif.member('capacity', '<Q'),
    StructSpecif.member('grainSize', '<Q'),
    StructSpecif.member('descriptorOffset', '<Q'),
    StructSpecif.member('descriptorSize', '<Q'),
    StructSpecif.member('numGTEsPerGT', '<I'),
    StructSpecif.member('rgdOffset', '<Q'),
    StructSpecif.member('gdOffset', '<Q'),
    StructSpecif.member('overHead', '<Q'),
    StructSpecif.member('uncleanShutdown', 'ba:1'),
    StructSpecif.member('singleEndLineChar', 'ba:1'),
    StructSpecif.member('nonEndLineChar', 'ba:1'),
    StructSpecif.member('doubleEndLineChar1', 'ba:1'),
    StructSpecif.member('doubleEndLineChar2', 'ba:1'),
    StructSpecif.member('compressAlgorithm', '<H'),
    StructSpecif.member('pad', 'ba:443')
]))
StructFactory.register_structure(StructSpecif('COWDisk_Header', [
    StructSpecif.member('magicNumber', '<I'),
    StructSpecif.member('version', '<I'),
    StructSpecif.member('flags', '<I'),
    StructSpecif.member('numSectors', '<I'),
    StructSpecif.member('grainSize', '<I'),
    StructSpecif.member('gdOffset', '<I'),
    StructSpecif.member('numGDEntries', '<I'),
    StructSpecif.member('freeSector', '<I'),
    StructSpecif.member('parentFileName', 'ba:1024'), #define COWDISK_MAX_PARENT_FILELEN 1024
    StructSpecif.member('parentGeneration', '<I'),
    StructSpecif.member('generation', '<I'),
    StructSpecif.member('name', 'ba:60'), #define COWDISK_MAX_NAME_LEN 60
    StructSpecif.member('description', 'ba:512'), #define COWDISK_MAX_DESC_LEN 512
    StructSpecif.member('savedGeneration', '<I'),
    StructSpecif.member('reserved', 'ba:8'),
    StructSpecif.member('uncleanShutdown', '<I'),
    StructSpecif.member('padding', 'ba:396')
]))
StructFactory.register_structure(StructSpecif('Marker', [
    StructSpecif.member('val', '<Q'),
    StructSpecif.member('size', '<I'),
    StructSpecif.member('type', '<I')
]))
StructFactory.register_structure(StructSpecif('GrainMarker', [
    StructSpecif.member('lba', '<Q'),
    StructSpecif.member('size', '<I'),
    StructSpecif.member('data', '<B')
]))
StructFactory.register_structure(StructSpecif('EOSMarker', [
    StructSpecif.member('val', '<Q'),
    StructSpecif.member('size', '<I'),
    StructSpecif.member('type', '<I'),
    StructSpecif.member('pad', 'ba:496')
]))
StructFactory.register_structure(StructSpecif('MetaDataMarker', [
    StructSpecif.member('numSectors', '<Q'),
    StructSpecif.member('size', '<I'),
    StructSpecif.member('type', '<I'),
    StructSpecif.member('pad', 'ba:496'),
    StructSpecif.member('metadata', '<B')
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
    return ('VMware4 disk image' in container.mime_text)
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
        vmdk_header = StructFactory.obj_from_file('SparseExtentHeader', f)
        LGR.info(StructFactory.obj_to_str(vmdk_header))
    # TODO : implement raw disk extraction
    raise NotImplementedError
    return []
#-------------------------------------------------------------------------------
# action_group()
#   /!\ public mandatory function that the module must define /!\
#   \brief returns module action group
#-------------------------------------------------------------------------------
def action_group():
    return ActionGroup('vmdk', {})
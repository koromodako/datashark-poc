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
import os.path
from dissection.container                import Container
from dissection.structure                import StructSpecif
from dissection.structure                import StructFactory
from utils.helpers.logging               import todo
from utils.helpers.logging               import get_logger
from utils.helpers.action_group          import ActionGroup
from dissection.helpers.descriptor_file  import DescriptorFile
#===============================================================================
# GLOBALS / CONFIG
#===============================================================================
LGR = get_logger(__name__)
SECTOR_SZ = 512 # bytes
StructFactory.register_structure(StructSpecif('SparseExtentHeader', [
    StructSpecif.member('magicNumber', 'ba:4'),
    StructSpecif.member('version', '<I'),
    StructSpecif.member('flags', '<I'),
    StructSpecif.member('capacity', '<Q'),          # in sectors unit
    StructSpecif.member('grainSize', '<Q'),         # in sectors unit
    StructSpecif.member('descriptorOffset', '<Q'),  # in sectors unit
    StructSpecif.member('descriptorSize', '<Q'),    # in sectors unit
    StructSpecif.member('numGTEsPerGT', '<I'),
    StructSpecif.member('rgdOffset', '<Q'),         # in sectors unit
    StructSpecif.member('gdOffset', '<Q'),          # in sectors unit
    StructSpecif.member('overHead', '<Q'),          # in sectors unit
    StructSpecif.member('uncleanShutdown', 'ba:1'),
    StructSpecif.member('singleEndLineChar', 'ba:1'),
    StructSpecif.member('nonEndLineChar', 'ba:1'),
    StructSpecif.member('doubleEndLineChar1', 'ba:1'),
    StructSpecif.member('doubleEndLineChar2', 'ba:1'),
    StructSpecif.member('compressAlgorithm', '<H'),
    StructSpecif.member('pad', 'ba:433')
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
# PRIVATE FUNCTIONS
#===============================================================================
#-------------------------------------------------------------------------------
# __find_header
#-------------------------------------------------------------------------------
def __find_header(fp):
    LGR.debug('__find_header()')
    sparse_hdr = StructFactory.obj_from_file('SparseExtentHeader', fp)
    cowdsk_hdr = StructFactory.obj_from_file('COWDisk_Header', fp)
    if sparse_hdr is not None and sparse_hdr.magicNumber == b'KDMV': # VMDK
        return sparse_hdr
    elif cowdsk_hdr is not None and cowdsk_hdr.magicNumber == b'DWOC': # COWD
        return cowdsk_hdr
    return None
#-------------------------------------------------------------------------------
# __parse_descriptor_file
#-------------------------------------------------------------------------------
def __parse_descriptor_file(hdr, fp):
    LGR.debug('__parse_descriptor_file()')
    # read descriptor file from open file
    fp.seek(hdr.obj_size)
    df = b''
    while len(descriptor_file) == 0 or descriptor_file[-1] != 0:
        descriptor_file += fp.read(1)
    descriptor_file = descriptor_file[:-1].decode('utf-8')
    # parse content
    return DescriptorFile(descriptor_file)
#-------------------------------------------------------------------------------
# __extract_extent
#-------------------------------------------------------------------------------
def __extract_sparse_extent(wdir, extent, ofp):
    LGR.debug('__extract_sparse_extent()')
    extent_path = os.path.join(wdir, extent.filename)
    if not os.path.isfile(extent_path):
        LGR.error('cannot find extent: {}'.format(extent_path))
    LGR.info('processing extent: {}'.format(extent_path))
    todo(LGR, 'implement here.')
#-------------------------------------------------------------------------------
# __dissect_monolithic_sparse
#-------------------------------------------------------------------------------
def __dissect_monolithic_sparse(wdir, extents, ofp):
    LGR.debug('__dissect_monolithic_sparse()')
    todo(LGR, 'implement here.')
#-------------------------------------------------------------------------------
# __dissect_monolithic_flat
#-------------------------------------------------------------------------------
def __dissect_monolithic_flat(wdir, extents, ofp):
    LGR.debug('__dissect_monolithic_flat()')
    todo(LGR, 'implement here.')
#-------------------------------------------------------------------------------
# __dissect_splitted_sparse
#-------------------------------------------------------------------------------
def __dissect_splitted_sparse(wdir, extents, ofp):
    LGR.debug('__dissect_splitted_sparse()')
    todo(LGR, 'implement here.')
#-------------------------------------------------------------------------------
# __dissect_splitted_flat
#-------------------------------------------------------------------------------
def __dissect_splitted_flat(wdir, extents, ofp):
    LGR.debug('__dissect_splitted_flat()')
    todo(LGR, 'implement here.')
#-------------------------------------------------------------------------------
# __dissect
#-------------------------------------------------------------------------------
def __dissect(wdir, df, ifp, ofp):
    LGR.debug('__dissect()')
    if not df.is_valid():
        LGR.error('invalid DescriptorFile.')
        return False
    # retrieve parent filename if has one
    parent_filename = None
    if df.has_parent():
        parent_filename = df.parent_filename()
    # select extraction based on multiple criterions
    if df.is_monolithic():
        if df.is_sparse():
            __dissect_monolithic_sparse(wdir, df.extents, ofp)
        elif df.is_flat():
            __dissect_monolithic_flat(wdir, df.extents, ofp)
        else:
            LGR.error('disk should be either flat or sparse if monolithic.')
            return False
    elif df.is_2gb_splitted():
        if df.is_sparse():
            __dissect_splitted_sparse(wdir, df.extents, ofp)
        elif df.is_flat():
            __dissect_splitted_flat(wdir, df.extents, ofp)
        else:
            LGR.error('disk should be either flat or sparse if 2GB splitted.')
            return False
    elif df.is_using_physical_disk():
        todo(LGR, 'implement dissection of physical disks.')
    elif df.is_using_raw_device_mapping():
        todo(LGR, 'implement dissection of raw devices mappings.')
    elif df.is_stream_optimized():
        todo(LGR, 'implement dissection of stream optimized disks.')
    elif df.is_esx_disk(): 
        todo(LGR, 'implement dissection of ESX disk.')
    else:
        LGR.error('unhandled disk type')
#===============================================================================
# PUBLIC FUNCTIONS
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
        'application/octet-stream', # .vmdk files
        'text/plain'                # .vmx files
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
    if 'VMware4 disk image' in container.mime_text:
        fp = container.ifileptr()
        hdr = __find_header(fp)
        fp.close()
        return (hdr is not None)
    elif container.path.endswith('.vmx'):
        fp = container.ifileptr()
        df = DescriptorFile(fp.read().decode('utf-8'))
        fp.close()
        return (df.is_valid())
    #else:
    return False
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
    containers = []
    wdir = container.wdir()
    ifp = container.ifileptr()
    ofp = container.ofileptr()
    hdr = __find_header(ifp)
    # find and parse descriptor file
    if hdr is not None and hdr.obj_type == 'SparseExtentHeader':
        df = __parse_descriptor_file(hdr, ifp)
    else:
        ifp.seek(0)
        df = DescriptorFile(ifp.read().decode('utf-8'))
    # dissect
    if not __dissect(wdir, df, ifp, ofp):
        LGR.warning('failed to dissect vmx/vmdk.')
    ofp.close()
    ifp.close()
    return containers
#-------------------------------------------------------------------------------
# action_group()
#   /!\ public mandatory function that the module must define /!\
#   \brief returns module action group
#-------------------------------------------------------------------------------
def action_group():
    #---------------------------------------------------------------------------
    # __action_header
    #---------------------------------------------------------------------------
    def __action_header(keywords, args):
        for f in args.files:
            if not os.path.isfile(f):
                continue
            with open(f, 'rb') as fp:
                hdr = __find_header(fp)
                if hdr is None:
                    LGR.error('no valid header found.')
                else:
                    LGR.info(StructFactory.obj_to_str(hdr))
    #---------------------------------------------------------------------------
    # __action_descfile
    #---------------------------------------------------------------------------
    def __action_descfile(keywords, args):
        for f in args.files:
            if not os.path.isfile(f):
                continue
            with open(f, 'rb') as fp:
                hdr = __find_header(fp)
                if hdr is None:
                    LGR.error('no valid header found.')
                else:
                    df = __parse_descriptor_file(hdr, fp)
                    if not df.is_valid():
                        LGR.error('no valid DescriptorFile found.')
                    else:
                        LGR.info(df.to_str())
    #---------------------------------------------------------------------------
    # ActionGroup
    #---------------------------------------------------------------------------
    return ActionGroup('vmdk', {
        'header': ActionGroup.action(__action_header, 'display vmdk sparse header.'),
        'descfile': ActionGroup.action(__action_descfile, 'display description file if found.')
    })
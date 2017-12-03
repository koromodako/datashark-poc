# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# =============================================================================
# IMPORTS
# =============================================================================
import os.path
from dissection.container import Container
from dissection.structure import StructSpecif
from dissection.structure import StructFactory
from utils.helpers.logging import todo
from utils.helpers.logging import get_logger
from utils.helpers.binary_file import BinaryFile
from utils.helpers.action_group import ActionGroup
from dissection.helpers.vmdk.gd import GrainDirectory
from dissection.helpers.vmdk.gd import SECTOR_SZ
from dissection.helpers.vmdk.descriptor_file import DescriptorFile
# =============================================================================
# GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
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
    StructSpecif.member('pad', 'ba:433', load=False)
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
    # define COWDISK_MAX_PARENT_FILELEN 1024
    StructSpecif.member('parentFileName', 'ba:1024'),
    StructSpecif.member('parentGeneration', '<I'),
    StructSpecif.member('generation', '<I'),
    # define COWDISK_MAX_NAME_LEN 60
    StructSpecif.member('name', 'ba:60'),
    # define COWDISK_MAX_DESC_LEN 512
    StructSpecif.member('description', 'ba:512'),
    StructSpecif.member('savedGeneration', '<I'),
    StructSpecif.member('reserved', 'ba:8'),
    StructSpecif.member('uncleanShutdown', '<I'),
    StructSpecif.member('padding', 'ba:396', load=False)
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
    StructSpecif.member('pad', 'ba:496', load=False)
]))
StructFactory.register_structure(StructSpecif('MetaDataMarker', [
    StructSpecif.member('numSectors', '<Q'),
    StructSpecif.member('size', '<I'),
    StructSpecif.member('type', '<I'),
    StructSpecif.member('pad', 'ba:496', load=False),
    StructSpecif.member('metadata', '<B')
]))
# =============================================================================
# PRIVATE FUNCTIONS
# =============================================================================


def __find_header(bf):
    # -------------------------------------------------------------------------
    # __find_header
    # -------------------------------------------------------------------------
    LGR.debug('__find_header()')

    sparse_hdr = StructFactory.obj_from_file('SparseExtentHeader', bf)
    cowdsk_hdr = StructFactory.obj_from_file('COWDisk_Header', bf)

    if sparse_hdr is not None and sparse_hdr.magicNumber == b'KDMV':    # VMDK
        return sparse_hdr
    elif cowdsk_hdr is not None and cowdsk_hdr.magicNumber == b'DWOC':  # COWD
        return cowdsk_hdr

    return None


def __parse_descriptor_file(hdr, bf):
    # -------------------------------------------------------------------------
    # __parse_descriptor_file
    # -------------------------------------------------------------------------
    LGR.debug('__parse_descriptor_file()')
    # read descriptor file from open file
    bf.seek(hdr.descriptorOffset * SECTOR_SZ)
    df_buf = bf.read(hdr.descriptorSize * SECTOR_SZ)
    df_eos = df_buf.index(b'\x00')
    df_str = df_buf[:df_eos].decode('utf-8')
    # parse content
    return DescriptorFile(df_str)


def __extract_sparse_extent(wdir, extent, obf):
    # -------------------------------------------------------------------------
    # __extract_extent
    # -------------------------------------------------------------------------
    LGR.debug('__extract_sparse_extent()')

    extent_path = os.path.join(wdir, extent.filename)
    if not BinaryFile.exists(extent_path):
        LGR.error('cannot find extent: {}'.format(extent_path))
        return False

    LGR.info('processing extent: {}'.format(extent_path))
    path = os.path.join(wdir, extent.filename)
    bf = BinaryFile(path, 'r')

    hdr = __find_header(bf)
    if hdr is None or hdr.obj_type != 'SparseExtentHeader':
        bf.close()
        return False

    GD = GrainDirectory(hdr, bf)

    num_sectors = hdr.capacity // SECTOR_SZ
    num_grains =  num_sectors // hdr.grainSize

    LGR.info('extracting {} grains from extent...'.format(num_grains))
    for gidx in range(num_grains):
        if (gidx+1) % 10 == 0:
            LGR.info('{}/{} grains extracted.'.format(gidx+1, num_grains))
        grain = GD.read_grain(gidx*hdr.grainSize)
        obf.write(grain) # output grain

    bf.close()
    return True

def __dissect_monolithic_sparse(wdir, extents, obf):
    # -------------------------------------------------------------------------
    # __dissect_monolithic_sparse
    # -------------------------------------------------------------------------
    LGR.debug('__dissect_monolithic_sparse()')

    total_sectors = sum([extent.size for extent in extents]) // SECTOR_SZ

    for extent in extents:
        extent_sectors = extent.size // SECTOR_SZ
        LGR.info('extracting {} of {} sectors.'.format(extent_sectors,
                                                       total_sectors))
        if not __extract_sparse_extent(wdir, extent, obf):
            LGR.error('sparse extent extraction failed!')
            return False

    return True


def __dissect_monolithic_flat(wdir, extents, obf):
    # -------------------------------------------------------------------------
    # __dissect_monolithic_flat
    # -------------------------------------------------------------------------
    LGR.debug('__dissect_monolithic_flat()')
    todo(LGR, 'implement here.')


def __dissect_splitted_sparse(wdir, extents, obf):
    # -------------------------------------------------------------------------
    # __dissect_splitted_sparse
    # -------------------------------------------------------------------------
    LGR.debug('__dissect_splitted_sparse()')
    todo(LGR, 'implement here.')


def __dissect_splitted_flat(wdir, extents, obf):
    # -------------------------------------------------------------------------
    # __dissect_splitted_flat
    # -------------------------------------------------------------------------
    LGR.debug('__dissect_splitted_flat()')
    todo(LGR, 'implement here.')


def __dissect(wdir, df, ibf, obf):
    # -------------------------------------------------------------------------
    # __dissect
    # -------------------------------------------------------------------------
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
            if not __dissect_monolithic_sparse(wdir, df.extents, obf):
                return False

        elif df.is_flat():
            __dissect_monolithic_flat(wdir, df.extents, obf)
        else:
            LGR.error('disk should be either flat or sparse if monolithic.')
            return False

    elif df.is_2gb_splitted():
        if df.is_sparse():
            __dissect_splitted_sparse(wdir, df.extents, obf)
        elif df.is_flat():
            __dissect_splitted_flat(wdir, df.extents, obf)
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
        return False

    return True
# =============================================================================
# PUBLIC FUNCTIONS
# =============================================================================


def mimes():
    # -------------------------------------------------------------------------
    # mimes
    #   /!\ public mandatory function that the module must define /!\
    #   \brief returns a list of mime types that this dissector can handle
    #   \return [list(str)]
    # -------------------------------------------------------------------------
    LGR.debug('mimes()')
    return [
        'application/octet-stream',     # .vmdk files
        'text/plain'                    # .vmx files
    ]


def configure(config):
    # -------------------------------------------------------------------------
    # configure
    #   /!\ public mandatory function that the module must define /!\
    #   \brief configures the dissector internal parameters
    #   \param [list(tuple(option, value))] config
    #       configuration taken from Datashark's INI file if found.
    #       config might be None or empty.
    # -------------------------------------------------------------------------
    LGR.debug('configure()')
    return True


def can_dissect(container):
    # -------------------------------------------------------------------------
    # can_dissect
    #   /!\ public mandatory function that the module must define /!\
    #   \brief returns true if dissector can effectively dissect given
    #          container
    #   \param [Container] container
    #   \return [bool]
    # -------------------------------------------------------------------------
    LGR.debug('can_dissect()')
    if 'VMware4 disk image' in container.mime_text:
        bf = container.ibf()
        hdr = __find_header(bf)
        bf.close()
        return (hdr is not None)

    elif container.path.endswith('.vmx'):
        bf = container.ibf()
        df = DescriptorFile(bf.read_text())
        bf.close()
        return (df.is_valid())

    return False


def dissect(container):
    # -------------------------------------------------------------------------
    # dissect
    #   /!\ public mandatory function that the module must define /!\
    #   \brief realize the dissection of the container and returns a list of
    #          containers found in the dissected container
    #   \param
    #   \return [list(Container)]
    # -------------------------------------------------------------------------
    LGR.debug('dissect()')

    containers = []
    wdir = container.wdir()
    ibf = container.ibf()
    obf = container.obf()
    hdr = __find_header(ibf)
    # find and parse descriptor file
    if hdr is not None and hdr.obj_type == 'SparseExtentHeader':
        df = __parse_descriptor_file(hdr, ibf)
    else:
        ibf.seek(0)
        df = DescriptorFile(ibf.read_text())
    # dissect
    if not __dissect(wdir, df, ibf, obf):
        LGR.warning('failed to dissect vmx/vmdk.')
    else:
        containers.append(Container(obf.abspath, 'disk.raw'))

    obf.close()
    ibf.close()
    return containers


def action_group():
    # -------------------------------------------------------------------------
    # action_group()
    #   /!\ public mandatory function that the module must define /!\
    #   \brief returns module action group
    # -------------------------------------------------------------------------
    LGR.debug('action_group()')

    def __action_header(keywords, args):
        # ---------------------------------------------------------------------
        # __action_header
        # ---------------------------------------------------------------------
        LGR.debug('__action_header()')
        for f in args.files:

            if not BinaryFile.exists(f):
                continue

            bf = BinaryFile(f, 'r')

            hdr = __find_header(bf)
            if hdr is None:
                LGR.error('no valid header found.')
                bf.close()
                continue

            bf.close()
            LGR.info(hdr.to_str())

    def __action_descfile(keywords, args):
        # ---------------------------------------------------------------------
        # __action_descfile
        # ---------------------------------------------------------------------
        LGR.debug('__action_descfile()')
        for f in args.files:
            if not BinaryFile.exists(f):
                continue

            bf = BinaryFile(f, 'r')

            hdr = __find_header(bf)
            if hdr is None:
                LGR.error('no valid header found.')
                bf.close()
                continue

            if hdr.obj_type != 'SparseExtentHeader':
                LGR.warning('only sparse extents have an embedded '
                            'description file.')
                bf.close()
                continue

            df = __parse_descriptor_file(hdr, bf)
            if not df.is_valid():
                LGR.error('invalid DescriptorFile found.')
                bf.close()
                continue

            bf.close()
            LGR.info(df.to_str())
    # -------------------------------------------------------------------------
    # ActionGroup
    # -------------------------------------------------------------------------
    return ActionGroup('vmdk', {
        'header': ActionGroup.action(__action_header,
                                     'display vmdk sparse header.'),
        'descfile': ActionGroup.action(__action_descfile,
                                       'display description file if found.')
    })

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: vmdk_disk.py
#     date: 2017-12-04
#   author: paul.dautry
#  purpose:
#
#  license:
#    Datashark <progdesc>
#    Copyright (C) 2017 paul.dautry
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
#  IMPORTS
# =============================================================================
from utils.logging import get_logger
from dissection.structure import StructSpecif
from dissection.structure import StructFactory
from helpers.vmdk.descriptor_file import DescriptorFile
# =============================================================================
# GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
S_SPARSE_EXTENT_HDR = 'SparseExtentHeader'
StructFactory.register_structure(StructSpecif(S_SPARSE_EXTENT_HDR, [
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
S_COWD_EXTENT_HDR = 'COWDisk_Header'
StructFactory.register_structure(StructSpecif(S_COWD_EXTENT_HDR, [
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
S_MARKER = 'Marker'
StructFactory.register_structure(StructSpecif(S_MARKER, [
    StructSpecif.member('val', '<Q'),
    StructSpecif.member('size', '<I'),
    StructSpecif.member('type', '<I')
]))
S_GRAIN_MARKER = 'GrainMarker'
StructFactory.register_structure(StructSpecif(S_GRAIN_MARKER, [
    StructSpecif.member('lba', '<Q'),
    StructSpecif.member('size', '<I'),
    StructSpecif.member('data', '<B')
]))
S_EOS_MARKER = 'EOSMarker'
StructFactory.register_structure(StructSpecif(S_EOS_MARKER, [
    StructSpecif.member('val', '<Q'),
    StructSpecif.member('size', '<I'),
    StructSpecif.member('type', '<I'),
    StructSpecif.member('pad', 'ba:496', load=False)
]))
S_METADATA_MARKER = 'MetaDataMarker'
StructFactory.register_structure(StructSpecif(S_METADATA_MARKER, [
    StructSpecif.member('numSectors', '<Q'),
    StructSpecif.member('size', '<I'),
    StructSpecif.member('type', '<I'),
    StructSpecif.member('pad', 'ba:496', load=False),
    StructSpecif.member('metadata', '<B')
]))
# =============================================================================
#  CLASSES
# =============================================================================

class VmdkDisk(object):
    SECTOR_SZ = 512  # bytes
    SIGN_VMDK = b'KDMV'
    SIGN_COWD = b'DWOC'
    # -------------------------------------------------------------------------
    # VmdkDisk
    # -------------------------------------------------------------------------
    def __init__(self, bf):
        super(VmdkDisk, self).__init__()
        self.bf = bf  # never close this bf you dont have the ownership

    def header(self):
        # ---------------------------------------------------------------------
        # header
        # ---------------------------------------------------------------------
        LGR.debug('VmdkDisk.header()')

        if hasattr(self, 'hdr'):
            return self.hdr  # lazy method

        self.hdr = None

        sparse_hdr = StructFactory.obj_from_file(S_SPARSE_EXTENT_HDR, self.bf)
        if sparse_hdr is not None:
            if sparse_hdr.magicNumber == self.SIGN_VMDK:
                self.hdr = sparse_hdr

        cowdsk_hdr = StructFactory.obj_from_file(S_COWD_EXTENT_HDR, self.bf)
        if cowdsk_hdr is not None:
            if cowdsk_hdr.magicNumber == self.SIGN_COWD:
                self.hdr = cowdsk_hdr

        return self.hdr

    def descriptor_file(self):
        # ---------------------------------------------------------------------
        # __parse_descriptor_file
        # ---------------------------------------------------------------------
        LGR.debug('VmdkDisk.descriptor_file()')

        if hasattr(self, 'df'):
            return self.df # lazy method

        if hasattr(self, 'hdr'):
            if self.header() is None: # requires header
                self.df = None
                return self.df

        self.bf.seek(self.hdr.descriptorOffset * self.SECTOR_SZ)
        df_buf = self.bf.read(self.hdr.descriptorSize * self.SECTOR_SZ)
        df_eos = df_buf.index(b'\x00')
        df_str = df_buf[:df_eos].decode('utf-8')

        self.df = DescriptorFile(df_str)

        return self.df

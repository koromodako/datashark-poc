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
from utils.structure_specif import UnionMember
from utils.structure_specif import SimpleMember
from utils.structure_specif import StructMember
from utils.structure_specif import StructSpecif
from utils.structure_specif import ByteArrayMember
from utils.structure_factory import StructFactory
from helpers.vmdk.descriptor_file import DescriptorFile
# =============================================================================
# GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
S_SPARSE_EXTENT_HDR = 'SparseExtentHeader'
StructFactory.st_register(StructSpecif(S_SPARSE_EXTENT_HDR, [
    ByteArrayMember('magicNumber', 4),
    SimpleMember('version', '<I'),
    SimpleMember('flags', '<I'),
    SimpleMember('capacity', '<Q'),          # in sectors unit
    SimpleMember('grainSize', '<Q'),         # in sectors unit
    SimpleMember('descriptorOffset', '<Q'),  # in sectors unit
    SimpleMember('descriptorSize', '<Q'),    # in sectors unit
    SimpleMember('numGTEsPerGT', '<I'),
    SimpleMember('rgdOffset', '<Q'),         # in sectors unit
    SimpleMember('gdOffset', '<Q'),          # in sectors unit
    SimpleMember('overHead', '<Q'),          # in sectors unit
    SimpleMember('uncleanShutdown', '?'),
    ByteArrayMember('singleEndLineChar', 1),
    ByteArrayMember('nonEndLineChar', 1),
    ByteArrayMember('doubleEndLineChar1', 1),
    ByteArrayMember('doubleEndLineChar2', 1),
    SimpleMember('compressAlgorithm', '<H'),
    ByteArrayMember('pad', 433, load=False)
]))
S_COWD_ROOT = 'COWDisk_root'
StructFactory.st_register(StructSpecif(S_COWD_ROOT, [
    SimpleMember('cylinders', '<I'),
    SimpleMember('heads', '<I'),
    SimpleMember('sectors', '<I')
]))
S_COWD_CHILD = 'COWDisk_child'
StructFactory.st_register(StructSpecif(S_COWD_CHILD, [
    # define COWDISK_MAX_PARENT_FILELEN 1024
    ByteArrayMember('parentFileName', 1024),
    SimpleMember('parentGeneration', '<I')
]))
S_COWD_EXTENT_HDR = 'COWDisk_Header'
StructFactory.st_register(StructSpecif(S_COWD_EXTENT_HDR, [
    SimpleMember('magicNumber', '<I'),
    SimpleMember('version', '<I'),
    SimpleMember('flags', '<I'),
    SimpleMember('numSectors', '<I'),
    SimpleMember('grainSize', '<I'),
    SimpleMember('gdOffset', '<I'),
    SimpleMember('numGDEntries', '<I'),
    SimpleMember('freeSector', '<I'),
    UnionMember('u', [
        StructMember('root', S_COWD_ROOT),
        StructMember('child', S_COWD_CHILD)
    ]),
    SimpleMember('generation', '<I'),
    # define COWDISK_MAX_NAME_LEN 60
    ByteArrayMember('name', 60),
    # define COWDISK_MAX_DESC_LEN 512
    ByteArrayMember('description', 512),
    SimpleMember('savedGeneration', '<I'),
    ByteArrayMember('reserved', 8),
    SimpleMember('uncleanShutdown', '<I'),
    ByteArrayMember('padding', 396, load=False)
]))
S_MARKER = 'Marker'
StructFactory.st_register(StructSpecif(S_MARKER, [
    SimpleMember('val', '<Q'),
    SimpleMember('size', '<I'),
    SimpleMember('type', '<I')
]))
S_GRAIN_MARKER = 'GrainMarker'
StructFactory.st_register(StructSpecif(S_GRAIN_MARKER, [
    SimpleMember('lba', '<Q'),
    SimpleMember('size', '<I'),
    SimpleMember('data', '<B')
]))
S_EOS_MARKER = 'EOSMarker'
StructFactory.st_register(StructSpecif(S_EOS_MARKER, [
    SimpleMember('val', '<Q'),
    SimpleMember('size', '<I'),
    SimpleMember('type', '<I'),
    ByteArrayMember('pad', 496, load=False)
]))
S_METADATA_MARKER = 'MetaDataMarker'
StructFactory.st_register(StructSpecif(S_METADATA_MARKER, [
    SimpleMember('numSectors', '<Q'),
    SimpleMember('size', '<I'),
    SimpleMember('type', '<I'),
    ByteArrayMember('pad', 496, load=False),
    SimpleMember('metadata', '<B')
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

    def header(self):   # LAZY METHOD
        # ---------------------------------------------------------------------
        # header
        # ---------------------------------------------------------------------
        LGR.debug('VmdkDisk.header()')

        if not hasattr(self, 'hdr'):
            self.hdr = None

            sparse_hdr = StructFactory.st_from_file(S_SPARSE_EXTENT_HDR, self.bf)
            if sparse_hdr is not None:
                if sparse_hdr.magicNumber == self.SIGN_VMDK:
                    self.hdr = sparse_hdr

            cowdsk_hdr = StructFactory.st_from_file(S_COWD_EXTENT_HDR, self.bf)
            if cowdsk_hdr is not None:
                if cowdsk_hdr.magicNumber == self.SIGN_COWD:
                    self.hdr = cowdsk_hdr

        return self.hdr

    def descriptor_file(self):  # LAZY METHOD
        # ---------------------------------------------------------------------
        # __parse_descriptor_file
        # ---------------------------------------------------------------------
        LGR.debug('VmdkDisk.descriptor_file()')

        if not hasattr(self, 'df'):
            self.df = None
            if not hasattr(self, 'hdr'):
                if self.header() is None: # requires header
                    return self.df

            self.bf.seek(self.hdr.descriptorOffset * self.SECTOR_SZ)
            df_buf = self.bf.read(self.hdr.descriptorSize * self.SECTOR_SZ)
            df_eos = df_buf.index(b'\x00')
            df_str = df_buf[:df_eos].decode('utf-8')

            self.df = DescriptorFile(df_str)

        return self.df

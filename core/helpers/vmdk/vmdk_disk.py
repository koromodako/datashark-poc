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
    # misc
    SECTOR_SZ = 512  # bytes
    GD_AT_END = 0xffffffffffffffff # uint64_t(-1)
    # signatures
    SIGN_VMDK = b'KDMV'
    SIGN_COWD = b'DWOC'
    # flags
    FLAG_VALID_NLT = (1 << 0)
    FLAG_USE_RGT = (1 << 1)
    FLAG_COMPRESSED = (1 << 16)
    FLAG_HAS_MARKERS = (1 << 17)
    # compression
    COMPRESSION_NONE = 0
    COMPRESSION_DEFLATE = 1
    # markers
    MARKER_EOS = 0
    MARKER_GD = 1
    MARKER_GT = 2
    MARKER_FOOTER = 3
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

    def has_footer(self):   # LAZY METHOD
        # ---------------------------------------------------------------------
        # has_footer
        # ---------------------------------------------------------------------
        LGR.debug('VmdkDisk.footer()')

        if not hasattr(self, 'has_ftr'):
            self.has_ftr = False

            if self.header() is None: # requires header
                return self.has_ftr

            if self.hdr.st_type != S_SPARSE_EXTENT_HDR:
                return self.has_ftr

            if self.hdr.gdOffset != self.GD_AT_END:
                return self.has_ftr

            compressed = (self.FLAG_HAS_MARKERS|self.FLAG_COMPRESSED)
            if (self.hdr.flags & compressed) == 0:
                return self.has_ftr

            if self.compressAlgorithm != COMPRESSION_DEFLATE:
                return self.has_ftr

            self.has_ftr = True

        return self.has_ftr

    def footer(self):   # LAZY METHOD
        # ---------------------------------------------------------------------
        # footer
        # ---------------------------------------------------------------------
        LGR.debug('VmdkDisk.footer()')

        if not hasattr(self, 'ftr'):
            self.ftr = None

            if self.header() is None: # requires header
                return self.ftr

            if not self.has_footer():
                return self.ftr

            vmdk_sz = self.bf.size()
            sector_cnt = vmdk_sz // self.SECTOR_SZ
            oft = (sector_cnt - 2) * self.SECTOR_SZ

            ftr = StructFactory.st_from_file(S_SPARSE_EXTENT_HDR, self.bf, oft)

            if ftr is None:
                return self.ftr

            self.ftr = ftr

        return self.ftr

    def descriptor_file(self):  # LAZY METHOD
        # ---------------------------------------------------------------------
        # descriptor_file
        # ---------------------------------------------------------------------
        LGR.debug('VmdkDisk.descriptor_file()')

        if not hasattr(self, 'df'):
            self.df = None

            if self.header() is None: # requires header
                return self.df

            if self.hdr.st_type != S_SPARSE_EXTENT_HDR:
                return self.df

            if self.hdr.descriptorOffset == 0:
                return self.df

            self.bf.seek(self.hdr.descriptorOffset * self.SECTOR_SZ)
            df_buf = self.bf.read(self.hdr.descriptorSize * self.SECTOR_SZ)
            df_eos = df_buf.index(b'\x00')
            df_str = df_buf[:df_eos].decode('utf-8')

            self.df = DescriptorFile(df_str)

        return self.df

    def metadata(self):
        # ---------------------------------------------------------------------
        # metadata
        # ---------------------------------------------------------------------
        LGR.debug('VmdkDisk.metadata()')

        if self.header() is None:
            LGR.error("cannot read disk header => cannot extract metadata.")
            return None

        if self.hdr.st_type == S_SPARSE_EXTENT_HDR:

            if self.has_footer():
                # -- Stream-Optimized Compressed Sparse Extents
                # load
                todo(LGR, "implement metadata extraction from "
                     "Stream-Optimized disks.")

            # -- Hosted Sparse Extents
            # loads redundant GD & GTs and normal GD & GTs in a single
            # bytearray
            self.bf.seek(self.hdr.rgdOffset * self.SECTOR_SZ)
            return self.bf.read(self.hdr.overHead * self.SECTOR_SZ)

        elif self.hdr.st_type == S_COWD_EXTENT_HDR:
            # -- ESX Server Sparse Extents
            # loads GD only
            self.bf.seek(self.hdr.gdOffset * self.SECTOR_SZ)
            gde_sz = SimpleMember('_', '<I').size()
            return self.bf.read(self.hdr.numGDEntries * gde_sz)

        LGR.error("unknown header type => cannot extract metadata. "
                  "<{}>".format(self.hdr.st_type))
        return None

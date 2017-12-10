# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: vhd_disk.py
#     date: 2017-12-09
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
from enum import Enum
from struct import calcsize
from utils.logging import todo
from utils.wrapper import trace
from utils.logging import get_logger
from utils.wrapper import lazy_getter
from utils.converting import unpack_one
from utils.structure_specif import ArrayMember
from utils.structure_specif import StructMember
from utils.structure_specif import SimpleMember
from utils.structure_specif import StructSpecif
from utils.structure_specif import ByteArrayMember
from utils.structure_factory import StructFactory
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
S_VHD_PARENT_LOCATOR_ENT = 'VHD_ParentLocatorEntry'
StructFactory.st_register(StructSpecif(S_VHD_PARENT_LOCATOR_ENT, [
    SimpleMember('platformCode', '>I'),
    SimpleMember('platformDataSpace', '>I'),
    SimpleMember('platformDataLength', '>I'),
    SimpleMember('reserved_0', '>I', load=False), # zeros (needs a check)
    SimpleMember('platformDataOft', '>Q')
]))
S_VHD_HEADER = 'VHDHeader'
StructFactory.st_register(StructSpecif(S_VHD_HEADER, [
    ByteArrayMember('cookie', 8),
    SimpleMember('dataOft', '>Q'),
    SimpleMember('tableOft', '>Q'),
    SimpleMember('hdrMajorVers', '>H'),
    SimpleMember('hdrMinorVers', '>H'),
    SimpleMember('maxTableEntries', '>I'),
    SimpleMember('blkSz', '>I'),
    SimpleMember('checksum', '>I'),
    ByteArrayMember('parentUuid', 16),
    SimpleMember('parentTimestamp', '>I'),
    ByteArrayMember('reserved_0', 4, load=False), # zeros (needs a check)
    ByteArrayMember('parentUnicodeName', 512),
    ArrayMember('parentLocators',
                StructMember('_', S_VHD_PARENT_LOCATOR_ENT),
                8),
    ByteArrayMember('reserved_1', 256, load=False) # zeros (needs a check)
]))
S_VHD_FOOTER = 'VHDFooter'
StructFactory.st_register(StructSpecif(S_VHD_FOOTER, [
    ByteArrayMember('cookie', 8),                   # identify creator
    SimpleMember('features', '>I'),                 # specific feature support
    SimpleMember('major', '>H'),                    # file format minor version
    SimpleMember('minor', '>H'),                    # file format major version
    SimpleMember('dataOft', '>Q'),                  # absolute offset to data
    SimpleMember('timestamp', '>I'),                # creation time
    ByteArrayMember('creatorApp', 4),               # creator application
    SimpleMember('creatorMajorVers', '>H'),         # creator app major version
    SimpleMember('creatorMinorVers', '>H'),         # creator app minor version
    SimpleMember('creatorHostOS', '>I'),            # creator app host OS
    SimpleMember('originalSz', '>Q'),               # size of hdd
    SimpleMember('currentSz', '>Q'),                # current size of hdd
    SimpleMember('diskGeomC', '>H'),                # cylinder size
    SimpleMember('diskGeomH', 'B'),                # head size
    SimpleMember('diskGeomS', 'B'),                # sector per track size
    SimpleMember('diskType', '>I'),                 # disk type enum
    SimpleMember('checksum', '>I'),                 # custom Microsoft checksum
    ByteArrayMember('uuid', 16),                    # UUID (parent linking)
    SimpleMember('savedState', '?'),                # in saved state or not ?
    ByteArrayMember('reserved_0', 427, load=False)  # zeros (needs a check)
]))
# =============================================================================
#  CLASSES
# =============================================================================


class VhdDiskCreatorHostOS(Enum):
    WINDOWS = 0x5769326b    # b'Wi2k'
    MAC = 0x4d616320        # b'Mac '


class VhdDiskType(Enum):
    NONE = 0
    RESERVED_0 = 1      # deprecated
    FIXED = 2
    DYNAMIC = 3
    DIFFERENCING = 4
    RESERVED_1 = 5      # deprecated
    RESERVED_2 = 6      # deprecated


class VhdDiskPlatformCode(Enum):
    NONE = 0x0
    WI2R = 0x57693272   # deprecated
    WI2K = 0x5769326b   # deprecated
    W2RU = 0x57327275
    W2KU = 0x57326b75
    MAC = 0x4d616320
    MACX = 0x4d616358


class VhdDisk(object):
    # -------------------------------------------------------------------------
    # VhdDisk
    # -------------------------------------------------------------------------
    # misc
    SECTOR_SZ = 512 # bytes
    # feature flags
    FEATURE_NONE = 0x0          # no special feature
    FEATURE_TEMPORARY = 0x1     # is it a temporary disk ?
    FEATURE_RESERVED = 0x2      # must always be set
    # all other should be 0

    def __init__(self, bf):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(VhdDisk, self).__init__()
        self.bf = bf

    @lazy_getter('_ftr')
    @trace(LGR)
    def footer(self):
        # ---------------------------------------------------------------------
        # footer
        # ---------------------------------------------------------------------
        return StructFactory.st_from_file(S_VHD_FOOTER, self.bf)

    @lazy_getter('_type')
    @trace(LGR)
    def type(self):
        # ---------------------------------------------------------------------
        # type
        # ---------------------------------------------------------------------
        if self.footer() is None:
            LGR.error("cannot parse footer => cannot extract disk type.")
            return None

        return VhdDiskType(self._ftr.diskType)

    @lazy_getter('_hdr')
    @trace(LGR)
    def header(self):
        # ---------------------------------------------------------------------
        # header
        # ---------------------------------------------------------------------
        if self.type() is None:
            LGR.error("failed to extract disk type.")
            return None

        if self._type not in [VhdDiskType.DYNAMIC, VhdDiskType.DIFFERENCING]:
            LGR.warning("cannot read header if disk is not dynamic nor "
                        "differencing.")
            return None

        return StructFactory.st_from_file(S_VHD_HEADER, self.bf, oft=512)

    @lazy_getter('_bat')
    @trace(LGR)
    def block_allocation_table(self):
        # ---------------------------------------------------------------------
        # block_allocation_table
        # ---------------------------------------------------------------------
        if self.header() is None:
            LGR.error("")
            return None

        self.bf.seek(self._hdr.tableOft)
        return self.bf.read(self._hdr.maxTableEntries * 4)

    @lazy_getter('_blk_cnt')
    @trace(LGR)
    def block_count(self):
        # ---------------------------------------------------------------------
        # block_count
        # ---------------------------------------------------------------------
        dtype = self.type()

        if dtype == VhdDiskType.FIXED:
            todo(LGR, "implement FIXED vhd type extraction.")

        elif dtype == VhdDiskType.DYNAMIC:
            if self.header() is None:
                LGR.error("dynamic vhd must have a header.")
                return None

            return self._hdr.maxTableEntries

        elif dtype == VhdDiskType.DIFFERENCING:
            todo(LGR, "implement DIFFERENCING vhd type extraction")

        LGR.error("unsupported vhd type.")
        return None

    @trace(LGR)
    def __read_dynamic_vhd_block(self, n):
        # ---------------------------------------------------------------------
        # __read_dynamic_vhd_block
        # ---------------------------------------------------------------------
        if self.block_allocation_table() is None:
            LGR.error("")
            return None

        blk_sz = self._hdr.blkSz
        bitmap_sz = (blk_sz // self.SECTOR_SZ) // 8

        fmt = '>I'
        sz = calcsize(fmt)
        blk_oft = unpack_one(fmt, self._bat[n*sz:(n+1)*sz])

        if blk_oft == 0xffffffff:
            data = b'\x00' * blk_sz
        else:
            self.bf.seek(blk_oft * self.SECTOR_SZ + bitmap_sz)
            data = self.bf.read(blk_sz)

        return data

    @trace(LGR)
    def read_block(self, n):
        # ---------------------------------------------------------------------
        # read_block
        # ---------------------------------------------------------------------
        dtype = self.type()

        if dtype == VhdDiskType.FIXED:
            todo(LGR, "implement FIXED vhd type extraction.")

        elif dtype == VhdDiskType.DYNAMIC:
            return self.__read_dynamic_vhd_block(n)

        elif dtype == VhdDiskType.DIFFERENCING:
            todo(LGR, "implement DIFFERENCING vhd type extraction")

        LGR.error("unsupported vhd type.")
        return None
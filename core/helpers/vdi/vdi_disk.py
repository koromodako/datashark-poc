# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: vdi_disk.py
#     date: 2017-12-07
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
from struct import calcsize
from utils.wrapper import trace
from utils.logging import get_logger
from utils.wrapper import lazy_getter
from utils.converting import unpack_one
from utils.structure_specif import SimpleMember
from utils.structure_specif import StructSpecif
from utils.structure_specif import ByteArrayMember
from utils.structure_factory import StructFactory
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
S_VDI_HDR = 'VDIHeader'
StructFactory.st_register(StructSpecif(S_VDI_HDR, [
    ByteArrayMember('magic', 0x40),
    ByteArrayMember('signature', 0x04),
    SimpleMember('vmajor', '<H'),
    SimpleMember('vminor', '<H'),
    SimpleMember('hdrSz', '<I'),
    SimpleMember('imgType', '<I'),
    SimpleMember('imgFlags', '<I'),
    ByteArrayMember('imgDesc', 0x100),
    SimpleMember('oftBlk', '<I'),
    SimpleMember('oftDat', '<I'),
    SimpleMember('numCylinders', '<I'),
    SimpleMember('numHeads', '<I'),
    SimpleMember('numSectors', '<I'),
    SimpleMember('sectorSz', '<I'),
    SimpleMember('pad0', '<I', load=False),
    SimpleMember('diskSz', '<Q'),                   # unit: B
    SimpleMember('blkSz', '<I'),
    SimpleMember('blkExtraDat', '<I'),
    SimpleMember('numBlkInHdd', '<I'),
    SimpleMember('numBlkAllocated', '<I'),
    ByteArrayMember('vdiUuid', 0x10),
    ByteArrayMember('lastSnapUuid', 0x10),
    ByteArrayMember('linkUuid', 0x10),
    ByteArrayMember('parentUuid', 0x10),
    ByteArrayMember('pad1', 0x38, load=False)
]))
# =============================================================================
#  CLASSES
# =============================================================================


class VdiDisk(object):
    VDI_SIGN = b'\x7f\x10\xda\xbe'
    # -------------------------------------------------------------------------
    # VdiDisk
    # -------------------------------------------------------------------------
    def __init__(self, bf):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(VdiDisk, self).__init__()
        self.bf = bf

    @lazy_getter('_hdr')
    @trace(LGR)
    def header(self):
        # ---------------------------------------------------------------------
        # header
        # ---------------------------------------------------------------------
        hdr = StructFactory.st_from_file(S_VDI_HDR, self.bf)
        if hdr is None:
            return hdr

        if hdr.signature != self.VDI_SIGN:
            return None

        return hdr

    @lazy_getter('_blk_map')
    @trace(LGR)
    def block_map(self):
        # ---------------------------------------------------------------------
        # block_map
        # ---------------------------------------------------------------------
        if self.header() is None:
            LGR.error("cannot parse header => cannot retrieve block map.")
            return None

        self.bf.seek(self._hdr.oftBlk)
        return self.bf.read(4 * self._hdr.numBlkInHdd)

    @trace(LGR)
    def read_block(self, n):
        # ---------------------------------------------------------------------
        # read_block
        # ---------------------------------------------------------------------
        if self.block_map() is None:
            LGR.error("cannot retrieve block map => cannot retrieve a block.")
            return None

        fmt = '<i'
        sz = calcsize(fmt)
        blk_oft = unpack_one(fmt, self._blk_map[n*sz:(n+1)*sz])

        if blk_oft < 0:
            return b'\x00' * self._hdr.blkSz

        self.bf.seek(self._hdr.oftDat + blk_oft)
        return self.bf.read(self._hdr.blkSz)

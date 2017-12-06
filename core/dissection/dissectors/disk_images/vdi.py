# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# =============================================================================
# IMPORTS
# =============================================================================
from utils.logging import get_logger
from utils.action_group import ActionGroup
from dissection.container import Container
from utils.structure_specif import SimpleMember
from utils.structure_specif import StructSpecif
from utils.structure_specif import ByteArrayMember
from utils.structure_factory import StructFactory
# =============================================================================
# GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
S_VDI_HDR = 'VDIHeader'
StructFactory.st_register(StructSpecif(S_VDI_HDR, [
    ByteArrayMember('magic', 0x40),
    ByteArrayMember('signature', 0x04),
    SimpleMember('vmajor', '<H'),
    SimpleMember('vminor', '<H'),
    SimpleMember('hdr_sz', '<I'),
    SimpleMember('img_type', '<I'),
    SimpleMember('img_flags', '<I'),
    ByteArrayMember('img_desc', 0x100),
    SimpleMember('oft_blk', '<I'),
    SimpleMember('oft_dat', '<I'),
    SimpleMember('num_cylinders', '<I'),
    SimpleMember('num_heads', '<I'),
    SimpleMember('num_sectors', '<I'),
    SimpleMember('sector_sz', '<I'),
    SimpleMember('pad0', '<I', load=False),
    SimpleMember('disk_sz', '<Q'),
    SimpleMember('blk_sz', '<I'),
    SimpleMember('blk_extra_dat', '<I'),
    SimpleMember('num_blk_in_hdd', '<I'),
    SimpleMember('num_blk_allocated', '<I'),
    ByteArrayMember('uuid_vdi', 0x10),
    ByteArrayMember('uuid_last_snap', 0x10),
    ByteArrayMember('uuid_link', 0x10),
    ByteArrayMember('uuid_parent', 0x10),
    ByteArrayMember('pad1', 0x38, load=False)
]))
# =============================================================================
# PRIVATE FUNCTIONS
# =============================================================================


def __header(fp):
    # -------------------------------------------------------------------------
    # __header
    # -------------------------------------------------------------------------
    return StructFactory.st_from_file(S_VDI_HDR, fp)
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
        'application/octet-stream'
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
    return ('VirtualBox Disk Image' in container.mime_text)


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
    ibf = container.ibfptr()
    vdi_header = __header(ibf)
    LGR.info(vdi_header.to_str())
    ibf.close()
    # TODO : implement raw disk extraction
    raise NotImplementedError
    return []


def action_group():
    # -------------------------------------------------------------------------
    # action_group()
    #   /!\ public mandatory function that the module must define /!\
    #   \brief returns module action group
    # -------------------------------------------------------------------------
    def __action_header(keywords, args):
        # ---------------------------------------------------------------------
        # __action_header
        # ---------------------------------------------------------------------
        for f in args.files:

            bf = BinaryFile(f, 'r')
            hdr = __header(bf)
            bf.close()

            if hdr is None:
                LGR.error("failed to read header, see previous logs for "
                          "error details.")
                continue

            LGR.info(hdr.to_str())
    # -------------------------------------------------------------------------
    # ActionGroup
    # -------------------------------------------------------------------------
    return ActionGroup('vdi', {
        'header': ActionGroup.action(__action_header, 'display vdi header.')
    })

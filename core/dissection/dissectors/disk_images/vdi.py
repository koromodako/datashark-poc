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
from utils.binary_file import BinaryFile
from utils.action_group import ActionGroup
from dissection.container import Container
from helpers.vdi.vdi_disk import VdiDisk
from helpers.vdi.vdi_extractor import VdiExtractor
# =============================================================================
# GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
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
    if 'VirtualBox Disk Image' not in container.mime_text:
        return False

    ibf = container.ibf()
    vdi = VdiDisk(ibf)
    vdi_hdr = vdi.header()
    ibf.close()

    if vdi_hdr is None:
        return False

    return True


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

    obf = container.obf()
    ibf = container.ibf()

    extractor = VdiExtractor(container.wdir(), VdiDisk(ibf), obf)
    if extractor.extract():
        containers.append(Container(obf.abspath, 'disk.raw'))
    else:
        LGR.error("failed to extract data from VDI.")

    obf.close()
    ibf.close()
    return containers


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
            vdi = VdiDisk(bf)
            vdi_hdr = vdi.header()
            bf.close()

            if vdi_hdr is None:
                LGR.error("failed to read header, see previous logs for "
                          "error details.")
                continue

            LGR.info(vdi_hdr.to_str())
    # -------------------------------------------------------------------------
    # ActionGroup
    # -------------------------------------------------------------------------
    return ActionGroup('vdi', {
        'header': ActionGroup.action(__action_header, "display vdi header.")
    })

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: vhd.py
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
from utils.wrapper import trace_func
from utils.binary_file import BinaryFile
from utils.action_group import ActionGroup
from dissection.container import Container
from helpers.vhd.vhd_disk import VhdDisk
from helpers.vhd.vhd_extractor import VhdExtractor
# =============================================================================
# GLOBAL
# =============================================================================
# =============================================================================
# GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# FUNCTIONS
# =============================================================================


@trace_func(LGR)
def mimes():
    # -------------------------------------------------------------------------
    # mimes
    #   /!\ public mandatory function that the module must define /!\
    #   \brief returns a list of mime types that this dissector can handle
    #   \return [list(str)]
    # -------------------------------------------------------------------------
    return [
        'application/octet-stream'
    ]


@trace_func(LGR)
def configure(config):
    # -------------------------------------------------------------------------
    # configure
    #   /!\ public mandatory function that the module must define /!\
    #   \brief configures the dissector internal parameters
    #   \param [list(tuple(option, value))] config
    #       configuration taken from Datashark's INI file if found.
    #       config might be None or empty.
    # -------------------------------------------------------------------------
    return True


@trace_func(LGR)
def can_dissect(container):
    # -------------------------------------------------------------------------
    # can_dissect
    #   /!\ public mandatory function that the module must define /!\
    #   \brief returns true if dissector can effectively dissect given
    #          container
    #   \param [Container] container
    #   \return [bool]
    # -------------------------------------------------------------------------
    if 'Microsoft Disk Image' not in container.mime_text:
        return False

    ibf = container.ibf()
    vhd = VhdDisk(ibf)

    if vhd.footer() is None:
        ibf.close()
        return False

    ibf.close()
    return True


@trace_func(LGR)
def dissect(container):
    # -------------------------------------------------------------------------
    # dissect
    #   /!\ public mandatory function that the module must define /!\
    #   \brief realize the dissection of the container and returns a list of
    #          containers found in the dissected container
    #   \param
    #   \return [list(Container)]
    # -------------------------------------------------------------------------
    containers = []

    obf = container.obf()
    ibf = container.ibf()

    extractor = VhdExtractor(container.wdir(), VhdDisk(ibf), obf)
    if extractor.extract():
        containers.append(Container(obf.abspath, 'disk.raw'))
    else:
        LGR.error("failed to extract data from VDI.")

    obf.close()
    ibf.close()
    return containers


@trace_func(LGR)
def action_group():
    # -------------------------------------------------------------------------
    # action_group()
    #   /!\ public mandatory function that the module must define /!\
    #   \brief returns module action group
    # -------------------------------------------------------------------------
    @trace_func(LGR)
    def __action_header(keywords, args):
        # ---------------------------------------------------------------------
        # __action_header
        # ---------------------------------------------------------------------
        for f in args.files:

            if not BinaryFile.exists(f):
                LGR.error("cannot open inexistant file: <{}>".format(f))
                continue

            bf = BinaryFile(f, 'r')
            vhd = VhdDisk(bf)
            hdr = vhd.header()
            bf.close()

            if hdr is None:
                LGR.error("fail to read VHD header.")
                continue

            LGR.info(hdr.to_str())

    @trace_func(LGR)
    def __action_footer(keywords, args):
        # ---------------------------------------------------------------------
        # __action_footer
        # ---------------------------------------------------------------------
        for f in args.files:

            if not BinaryFile.exists(f):
                LGR.error("cannot open inexistant file: <{}>".format(f))
                continue

            bf = BinaryFile(f, 'r')
            vhd = VhdDisk(bf)
            ftr = vhd.footer()
            bf.close()

            if ftr is None:
                LGR.error("fail to read VHD footer.")
                continue

            LGR.info(ftr.to_str())

    # -------------------------------------------------------------------------
    # ActionGroup
    # -------------------------------------------------------------------------
    return ActionGroup('vhd', {
        'header': ActionGroup.action(__action_header, "display vhd header."),
        'footer': ActionGroup.action(__action_footer, "display vhd footer.")
    })

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
from utils.logging import todo
from utils.logging import get_logger
from utils.wrapper import trace_func
from utils.binary_file import BinaryFile
from utils.action_group import ActionGroup
from dissection.container import Container
# dissection helpers
from helpers.vmdk.vmdk_disk import VmdkDisk
from helpers.vmdk.descriptor_file import DescriptorFile
from helpers.vmdk.flat_extent_extractor import FlatExtentExtractor
from helpers.vmdk.sparse_extent_extractor import SparseExtentExtractor
# =============================================================================
# GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# PRIVATE FUNCTIONS
# =============================================================================


@trace_func(LGR)
def __dissect_from_vmdk(wdir, vmdk, obf):
    # -------------------------------------------------------------------------
    # __dissect_from_vmdk
    #   handles both Hosted Sparse Extent & ESX Server Sparse Extent dissection
    # -------------------------------------------------------------------------
    df = vmdk.descriptor_file()

    if not df.is_valid():
        LGR.error("invalid descriptor file.")
        return False

    if df.is_sparse():
        see = SparseExtentExtractor(wdir, vmdk, obf)
        return see.extract()

    elif df.is_flat():
        fee = FlatExtentExtractor(wdir, vmdk, obf)
        return fee.extract()

    elif df.is_using_physical_disk():
        todo(LGR, 'implement dissection of physical disks.')

    elif df.is_using_raw_device_mapping():
        todo(LGR, 'implement dissection of raw devices mappings.')

    elif df.is_stream_optimized():
        todo(LGR, 'implement dissection of stream optimized disks.')

    elif df.is_esx_disk():
        todo(LGR, 'implement dissection of ESX disk.')

    else:
        LGR.error("unhandled disk type")
        return False

    return True


@trace_func(LGR)
def __dissect_from_vmx(wdir, df, obf):
    # -------------------------------------------------------------------------
    # __dissect_from_vmx
    # -------------------------------------------------------------------------
    todo(LGR, 'implement dissection from vmx file.')
# =============================================================================
# PUBLIC FUNCTIONS
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
        'application/octet-stream',     # .vmdk files
        'text/plain'                    # .vmx files
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
    if 'VMware4 disk image' in container.mime_text:
        bf = container.ibf()
        vmdk = VmdkDisk(bf)
        hdr = vmdk.header()
        bf.close()
        return (hdr is not None)

    elif container.path.endswith('.vmx'):
        bf = container.ibf()
        df = DescriptorFile(bf.read_text())
        bf.close()
        return (df.is_valid())

    return False


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
    wdir = container.wdir()
    ibf = container.ibf()
    obf = container.obf()
    vmdk = VmdkDisk(ibf)
    # find and parse descriptor file
    if vmdk.header() is None:
        ibf.seek(0)
        df = DescriptorFile(ibf.read_text())

        if __dissect_from_vmx(wdir, df, obf):
            containers.append(Container(obf.abspath, 'disk.raw'))
        else:
            LGR.warning('failed to dissect from vmx file.')

    else:
        if __dissect_from_vmdk(wdir, vmdk, obf):
            containers.append(Container(obf.abspath, 'disk.raw'))
        else:
            LGR.warning('failed to dissect from vmdk file.')

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
                continue

            bf = BinaryFile(f, 'r')
            vmdk = VmdkDisk(bf)
            hdr = vmdk.header()
            bf.close()

            if hdr is None:
                LGR.error("no valid header found.")
                continue

            LGR.info(hdr.to_str())

    @trace_func(LGR)
    def __action_descfile(keywords, args):
        # ---------------------------------------------------------------------
        # __action_descfile
        # ---------------------------------------------------------------------
        for f in args.files:
            if not BinaryFile.exists(f):
                continue

            bf = BinaryFile(f, 'r')
            vmdk = VmdkDisk(bf)

            if vmdk.header() is None:
                LGR.error("no valid header found.")
                bf.close()
                continue

            df = vmdk.descriptor_file()
            bf.close()

            if df is None:
                LGR.warning("only sparse extents have an embedded "
                            "description file.")
                continue

            if not df.is_valid():
                LGR.error("invalid DescriptorFile found.")
                continue

            LGR.info(df.to_str())
    # -------------------------------------------------------------------------
    # ActionGroup
    # -------------------------------------------------------------------------
    return ActionGroup('vmdk', {
        'header': ActionGroup.action(__action_header,
                                     "display vmdk sparse header."),
        'descfile': ActionGroup.action(__action_descfile,
                                       "display description file if found.")
    })

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: ext4.py
#     date: 2018-01-07
#   author: paul.dautry
#  purpose:
#
#  license:
#    Datashark <progdesc>
#    Copyright (C) 2018 paul.dautry
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
# IMPORTS
# =============================================================================
from utils.logging import get_logger
from utils.wrapper import trace_func
from utils.formatting import hexdump
from utils.binary_file import BinaryFile
from helpers.ext4.ext4 import Ext4FS
from utils.action_group import ActionGroup
from container.container import Container
from helpers.ext4.constants import Ext4FileType
# =============================================================================
# GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# PUBLIC FUNCTIONS
# =============================================================================
##
## @brief      returns a list of mime types that this dissector can handle
## @warning    public mandatory function that the module must define
##
## @return     a list of mime types
##
@trace_func(__name__)
def mimes():
    return [
        'application/octet-stream'
    ]
##
## @brief      configures the dissector internal parameters
## @warning    public mandatory function that the module must define
##
## @param      config  The configuration
##
## @return     { description_of_the_return_value }
##
@trace_func(__name__)
def configure(config):
    return True
##
## @brief      Determines ability to dissect given container.
## @warning    public mandatory function that the module must define
##
## @param      container  The container
##
## @return     True if able to dissect, False otherwise.
##
@trace_func(__name__)
def can_dissect(container):
    if 'Linux rev 1.0 ext4 filesystem data' not in container.mime_text:
        return False

    ibf = container.ibf()
    fs = Ext4FS(ibf)
    valid = fs.is_valid()
    ibf.close()

    return valid
##
## @brief      performs the dissection of the container and returns a list of
##             containers found in the dissected container
## @warning    public mandatory function that the module must define
##
## @param      container  The container
##
## @return     a list of containers
##
@trace_func(__name__)
def dissect(container):
    containers = []

    #obf = container.obf('vdi.raw')
    #ibf = container.ibf()

    todo(LGR, "implement ext4.dissect()", no_raise=True)

    #obf.close()
    #ibf.close()

    return containers
##
## @brief      { function_description }
## @warning    public mandatory function that the module must define
##
## @return     { description_of_the_return_value }
##
@trace_func(__name__)
def action_group():
    ##
    ## @brief      { function_description }
    ##
    ## @param      keywords  The keywords
    ## @param      args      The arguments
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace_func(__name__)
    def __action_superblock(keywords, args):
        for f in args.files:

            if not BinaryFile.exists(f):
                LGR.warn("invalid path <{}> => skipped.".format(f))
                continue

            sb = None
            with BinaryFile(f, 'r') as bf:
                fs = Ext4FS(bf)

                if not fs.is_valid():
                    LGR.warn("invalid fs or superblock.")
                    continue

                sb = fs.sb

            if sb is None:
                continue

            print(sb.st_to_str())

        return True
    ##
    ## @brief      { function_description }
    ##
    ## @param      keywords  The keywords
    ## @param      args      The arguments
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace_func(__name__)
    def __action_bg_desc(keywords, args):
        for f in args.files:

            if not BinaryFile.exists(f):
                LGR.warn("invalid path <{}> => skipped.".format(f))
                continue

            sb = None
            with BinaryFile(f, 'r') as bf:
                fs = Ext4FS(bf)

                if not fs.is_valid():
                    LGR.warn("invalid fs or superblock.")
                    continue

                bgds = fs.bgds

            for bgd in bgds:
                print(bgd.st_to_str())

        return True
    ##
    ## @brief      { function_description }
    ##
    ## @param      keywords  The keywords
    ## @param      args      The arguments
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace_func(__name__)
    def __action_inodes(keywords, args):
        for f in args.files:

            if not BinaryFile.exists(f):
                LGR.warn("invalid path <{}> => skipped.".format(f))
                continue

            with BinaryFile(f, 'r') as bf:
                fs = Ext4FS(bf)

                if not fs.is_valid():
                    LGR.warn("invalid fs or superblock.")
                    continue

                for inode in fs.inodes():
                    print(inode.st_to_str())

        return True
    ##
    ## @brief      { function_description }
    ##
    ## @param      keywords  The keywords
    ## @param      args      The arguments
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace_func(__name__)
    def __action_inode(keywords, args):
        for f in args.files:

            if not BinaryFile.exists(f):
                LGR.warn("invalid path <{}> => skipped.".format(f))
                continue

            with BinaryFile(f, 'r') as bf:
                fs = Ext4FS(bf)

                if not fs.is_valid():
                    LGR.warn("invalid fs or superblock.")
                    continue

                i = args.index
                if i is None:
                    LGR.error("this action requires an index to be specified "
                              "using --index option.")
                    return False

                try:
                    inode = fs.inode(i)
                except ValueError as e:
                    LGR.exception("you should try another index value.")
                    return False

                print(inode.st_to_str())

        return True
    ##
    ## @brief      { function_description }
    ##
    ## @param      keywords  The keywords
    ## @param      args      The arguments
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace_func(__name__)
    def __action_inode_blocks(keywords, args):
        for f in args.files:

            if not BinaryFile.exists(f):
                LGR.warn("invalid path <{}> => skipped.".format(f))
                continue

            with BinaryFile(f, 'r') as bf:
                fs = Ext4FS(bf)

                if not fs.is_valid():
                    LGR.warn("invalid fs or superblock.")
                    continue

                i = args.index
                if i is None:
                    LGR.error("this action requires an index to be specified "
                              "using --index option.")
                    return False

                try:
                    inode = fs.inode(i)
                except Exception as e:
                    LGR.exception("this inode index seems to be inexistant "
                                  "within given filesystem.")
                    continue

                k = 0
                for blk_id, blk in fs.inode_blocks(inode):
                    print("{}:".format(blk_id))
                    print(hexdump(blk, max_lines=args.max_lines))
                    k += 1

        return True

    ##
    ## @brief      { function_description }
    ##
    ## @param      keywords  The keywords
    ## @param      args      The arguments
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace_func(__name__)
    def __action_inode_block(keywords, args):
        for f in args.files:

            if not BinaryFile.exists(f):
                LGR.warn("invalid path <{}> => skipped.".format(f))
                continue

            with BinaryFile(f, 'r') as bf:
                fs = Ext4FS(bf)

                if not fs.is_valid():
                    LGR.warn("invalid fs or superblock.")
                    continue

                i = args.index
                if i is None:
                    LGR.error("this action requires an index to be specified "
                              "using --index option.")
                    return False

                o = args.offset
                if o is None:
                    LGR.error("this action requires an index to be specified "
                              "using --offset option.")
                    return False

                try:
                    inode = fs.inode(i)
                except Exception as e:
                    LGR.exception("this inode index seems to be inexistant "
                                  "within given filesystem.")
                    continue

                blk_id, blk = fs.inode_block(inode, o)
                if blk is None:
                    LGR.error("failed to retrieve file content block.")
                    return False

                print("{}:".format(blk_id))
                print(hexdump(blk, max_lines=args.max_lines))

        return True

    return ActionGroup('ext4', {
        'superblock': ActionGroup.action(__action_superblock,
                                         "display ext4 fs superblock."),
        'bg_desc': ActionGroup.action(__action_bg_desc,
                                      "perform block group desc action."),
        'inodes': ActionGroup.action(__action_inodes,
                                     "display all inodes present in the "
                                     "filesystem."),
        'inode': ActionGroup.action(__action_inode,
                                     "display seclected inode and additional "
                                     "information. This action requires an "
                                     "index to be specified using --index "
                                     "option."),
        'inode_blocks': ActionGroup.action(__action_inode_blocks,
                                           "display inode blocks. This action "
                                           "requires an index to be specified "
                                           "using --index option."),
        'inode_block': ActionGroup.action(__action_inode_block,
                                           "display inode blocks. This action "
                                           "requires an index and offset to "
                                           "be specified using --index and "
                                           "--offset options.")
    })

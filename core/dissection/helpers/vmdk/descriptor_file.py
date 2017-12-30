# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: descriptor_file.py
#    date: 2017-11-24
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
from utils.wrapper import trace
from utils.logging import get_logger
from dissection.helpers.vmdk.extent import Extent
# =============================================================================
# GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# CLASSES
# =============================================================================
##
## @brief      Class for descriptor file.
##
class DescriptorFile(object):
    K_CID = 'CID'
    K_VERSION = 'version'
    K_PARENT_CID = 'parentCID'
    K_CREATE_TYPE = 'createType'
    K_PARENT_FILENAME_HINT = 'parentFileNameHint'
    CID_NOPARENT = 'ffffffff'   # int32_t (~0x0)
    HEADER_KWDS = [
        K_CID,
        K_VERSION,
        K_PARENT_CID,
        K_CREATE_TYPE,
        K_PARENT_FILENAME_HINT
    ]
    PHY_CREATE_TYPES = [
        'fullDevice',
        'vmfsRaw',
        'partitionedDevice'
    ]
    RAW_DEV_MAP_CREATE_TYPES = [
        'vmfsRawDeviceMap',
        'vmfsPassthroughRawDeviceMap'
    ]
    STREAM_OPTIM_CREATE_TYPES = [
        'streamOptimized'
    ]
    CREATE_TYPES = (
        PHY_CREATE_TYPES +
        RAW_DEV_MAP_CREATE_TYPES +
        STREAM_OPTIM_CREATE_TYPES +
        [
            'monolithicFlat',
            'monolithicSparse',
            'vmfs',
            'vmfsSparse',
            'twoGbMaxExtentFlat',
            'twoGbMaxExtentSparse'
        ]
    )
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      s     { parameter_description }
    ##
    def __init__(self, s):
        super(DescriptorFile, self).__init__()
        self.extents = []
        self.ddb = {}
        self.__valid = (self.__parse(s) and self.__check())
    ##
    ## @brief      { function_description }
    ##
    ## @param      s     { parameter_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def __parse(self, s):
        for line in s.split('\n'):
            ok = False
            line = line.strip()
            # skip blank lines and comments
            if len(line) == 0 or line.startswith('#'):
                continue
            # check for header keywords
            for key in DescriptorFile.HEADER_KWDS:
                if line.startswith(key) and line.count('=') == 1:
                    setattr(self, key, line.split('=')[-1].strip())
                    ok = True
                    break
            # check for extents keywords
            for key in Extent.ACCESS_KWDS:
                if line.startswith(key):
                    extent = Extent(line)
                    if extent.is_valid():
                        self.extents.append(extent)
                    ok = True
                    break
            # check for disk database keyword
            if line.startswith('ddb.') and line.count('=') == 1:
                key = line.split('=')[0].strip().replace('ddb.', '')
                val = line.split('=')[-1].strip()
                self.ddb[key] = val[1:-1]
                continue
            # unhandled line
            if not ok:
                LGR.warn("unhandled descriptor file line: {}".format(l))
        # descriptor file parsing step is valid
        return True
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def __check(self):
        # check parentCID and parentFileNameHint
        if not hasattr(self, self.K_PARENT_CID):
            LGR.error("missing parentCID.")
            return False
        if self.has_parent():
            if not hasattr(self, self.K_PARENT_FILENAME_HINT):
                LGR.error("missing parentFileNameHint.")
                return False
        # check createType
        if not hasattr(self, self.K_CREATE_TYPE):
            LGR.error("missing createType in descriptor file.")
            return False
        createType = getattr(self, self.K_CREATE_TYPE)[1:-1]
        setattr(self, self.K_CREATE_TYPE, createType)
        if createType not in self.CREATE_TYPES:
            LGR.error("unhandled createType in descriptor file. ({})".format(
                getattr(self, self.K_CREATE_TYPE)))
            return False
        # descriptor file check step is valid
        return True
    ##
    ## @brief      Determines if valid.
    ##
    ## @return     True if valid, False otherwise.
    ##
    @trace()
    def is_valid(self):
        return self.__valid
    ##
    ## @brief      Determines if it has parent.
    ##
    ## @return     True if has parent, False otherwise.
    ##
    @trace()
    def has_parent(self):
        return (getattr(self, self.K_PARENT_CID) != self.CID_NOPARENT)
    ##
    ## @brief      Determines if monolithic.
    ##
    ## @return     True if monolithic, False otherwise.
    ##
    @trace()
    def is_monolithic(self):
        return ('monolithic' in getattr(self, self.K_CREATE_TYPE).lower())
    ##
    ## @brief      Determines if 2 gigabytes splitted.
    ##
    ## @return     True if 2 gigabytes splitted, False otherwise.
    ##
    @trace()
    def is_2gb_splitted(self):
        return ('twogbmaxextent' in getattr(self, self.K_CREATE_TYPE).lower())
    ##
    ## @brief      Determines if sparse.
    ##
    ## @return     True if sparse, False otherwise.
    ##
    @trace()
    def is_sparse(self):
        return ('sparse' in getattr(self, self.K_CREATE_TYPE).lower())
    ##
    ## @brief      Determines if esx disk.
    ##
    ## @return     True if esx disk, False otherwise.
    ##
    @trace()
    def is_esx_disk(self):
        return ('vmfs' in getattr(self, self.K_CREATE_TYPE).lower())
    ##
    ## @brief      Determines if using physical disk.
    ##
    ## @return     True if using physical disk, False otherwise.
    ##
    @trace()
    def is_using_physical_disk(self):
        return (getattr(self, self.K_CREATE_TYPE) in self.PHY_CREATE_TYPES)
    ##
    ## @brief      Determines if using raw device mapping.
    ##
    ## @return     True if using raw device mapping, False otherwise.
    ##
    @trace()
    def is_using_raw_device_mapping(self):
        createType = getattr(self, self.K_CREATE_TYPE)
        return (createType in self.RAW_DEV_MAP_CREATE_TYPES)
    ##
    ## @brief      Determines if stream optimized.
    ##
    ## @return     True if stream optimized, False otherwise.
    ##
    @trace()
    def is_stream_optimized(self):
        createType = getattr(self, self.K_CREATE_TYPE)
        return (createType in self.STREAM_OPTIM_CREATE_TYPES)
    ##
    ## @brief      { function_description }
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def parent_filename(self):
        if not hasattr(self, self.K_PARENT_FILENAME_HINT):
            return None

        return getattr(self, self.K_PARENT_FILENAME_HINT)
    ##
    ## @brief      Returns a string representation of the object.
    ##
    ## @return     String representation of the object.
    ##
    @trace()
    def to_str(self):
        text = "\nDescriptorFile:"
        text += "\n\theader:"
        for key in DescriptorFile.HEADER_KWDS:
            if hasattr(self, key):
                text += "\n\t\t+ {}: {}".format(key, getattr(self, key))

        text += "\n\textents:"
        for extent in self.extents:
            text += "\n\t\t + {}".format(extent.to_str())

        text += "\n\tddb:"
        for key, value in self.ddb.items():
            text += "\n\t\t + {}: {}".format(key, value)
        return text + "\n"

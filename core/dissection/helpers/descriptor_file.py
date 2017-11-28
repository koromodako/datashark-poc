#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#===============================================================================
# IMPORTS
#===============================================================================
from utils.helpers.logging import get_logger
#===============================================================================
# GLOBALS / CONFIG
#===============================================================================
LGR = get_logger(__name__)
#===============================================================================
# CLASSES
#===============================================================================
#-------------------------------------------------------------------------------
# Extent
#-------------------------------------------------------------------------------
class Extent(object):
    ACCESS_KWDS = [
        'RW',
        'RDONLY',
        'NOACCESS'
    ]
    FLAT_TYPES = [
        'FLAT', 
        'VMFS', 
        'VMFSRDM', 
        'VMFSRAW'
    ]
    TYPE_KWDS = FLAT_TYPES + [
        'SPARSE',
        'ZERO',
        'VMFSSPARSE'
    ]
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self, line):
        super(Extent, self).__init__()
        self.__valid = self.__parse(line)
    #---------------------------------------------------------------------------
    # __parse
    #---------------------------------------------------------------------------
    def __parse(self, line):
        LGR.debug('Extent.__parse()')
        pts = line.split(' ')
        if len(pts) < 4:
            LGR.warning('invalid extent: {}'.format(line))
            return False
        self.access = pts[0]
        if not self.access in Extent.ACCESS_KWDS:
            LGR.warning('invalid extent access: {}'.format(self.access))
            return False
        self.size = int(pts[1])
        self.type = pts[2]
        if not self.type in Extent.TYPE_KWDS:
            LGR.warning('invalid extent type: {}'.format(self.type))
            return False
        self.filename = pts[3][1:-1]
        self.offset = None # invalid offset
        if len(pts) == 5:
            self.offset = int(pts[4])
        return True
    #---------------------------------------------------------------------------
    # is_valid
    #---------------------------------------------------------------------------
    def is_valid(self):
        return self.__valid
    #---------------------------------------------------------------------------
    # is_flat
    #---------------------------------------------------------------------------
    def is_flat(self):
        LGR.debug('Extent.is_flat()')
        return (self.type in Extent.FLAT_TYPES)
    #---------------------------------------------------------------------------
    # to_str
    #---------------------------------------------------------------------------
    def to_str(self):
        return '{} {} {} {} {}'.format(self.access, self.size, self.type, 
            self.filename, self.offset if self.offset is not None else '')
#-------------------------------------------------------------------------------
# DescriptorFile
#-------------------------------------------------------------------------------
class DescriptorFile(object):
    K_CID = 'CID'
    K_VERSION = 'version'
    K_PARENT_CID = 'parentCID'
    K_CREATE_TYPE = 'createType'
    K_PARENT_FILENAME_HINT = 'parentFileNameHint'
    CID_NOPARENT = 'ffffffff' # int32_t (~0x0)
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
    ])
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self, s):
        super(DescriptorFile, self).__init__()
        self.extents = []
        self.ddb = {}
        self.__valid = (self.__parse(s) and self.__check())
    #---------------------------------------------------------------------------
    # __parse
    #---------------------------------------------------------------------------
    def __parse(self, s):
        LGR.debug('DescriptorFile.__parse()')
        for l in s.split('\n'):
            ok = False
            l = l.strip()
            # skip blank lines and comments
            if len(l) == 0 or l.startswith('#'):
                continue
            # check for header keywords
            for key in DescriptorFile.HEADER_KWDS:
                if l.startswith(key) and l.count('=') == 1:
                    setattr(self, key, l.split('=')[-1].strip())
                    ok = True
                    break
            # check for extents keywords
            for key in Extent.ACCESS_KWDS:
                if l.startswith(key):
                    extent = Extent(l)
                    if extent.is_valid():
                        self.extents.append(extent)
                    ok = True
                    break
            # check for disk database keyword
            if l.startswith('ddb.') and l.count('=') == 1:
                key = l.split('=')[0].strip().replace('ddb.', '')
                val = l.split('=')[-1].strip()
                self.ddb[key] = val[1:-1]
                continue
            # unhandled line
            if not ok:
                LGR.warning('unhandled descriptor file line: {}'.format(l))
        # descriptor file parsing step is valid
        return True
    #---------------------------------------------------------------------------
    # __check
    #---------------------------------------------------------------------------
    def __check(self):
        LGR.debug('DescriptorFile.__check()')
        # check parentCID and parentFileNameHint
        if not hasattr(self, self.K_PARENT_CID):
            LGR.error('missing parentCID.')
            return False
        if self.has_parent():
            if not hasattr(self, self.K_PARENT_FILENAME_HINT):
                LGR.error('missing parentFileNameHint.')
                return False
        # check createType
        if not hasattr(self, self.K_CREATE_TYPE):
            LGR.error('missing createType in descriptor file.')
            return False
        createType = getattr(self, self.K_CREATE_TYPE)[1:-1]
        setattr(self, self.K_CREATE_TYPE, createType)
        if not createType in self.CREATE_TYPES:
            LGR.error('unhandled createType in descriptor file. ({})'.format(
                getattr(self, self.K_CREATE_TYPE)))
            return False
        # descriptor file check step is valid
        return True
    #---------------------------------------------------------------------------
    # is_valid
    #---------------------------------------------------------------------------
    def is_valid(self):
        return self.__valid
    #---------------------------------------------------------------------------
    # has_parent
    #---------------------------------------------------------------------------
    def has_parent(self):
        LGR.debug('DescriptorFile.has_parent()')
        return (getattr(self, self.K_PARENT_CID) != self.CID_NOPARENT)
    #---------------------------------------------------------------------------
    # is_monolithic
    #---------------------------------------------------------------------------
    def is_monolithic(self):
        LGR.debug('DescriptorFile.is_monolithic()')
        return ('monolithic' in getattr(self, self.K_CREATE_TYPE).lower())
    #---------------------------------------------------------------------------
    # is_2gb_splitted
    #---------------------------------------------------------------------------
    def is_2gb_splitted(self):
        LGR.debug('DescriptorFile.is_2gb_splitted()')
        return ('twogbmaxextent' in getattr(self, self.K_CREATE_TYPE).lower())
    #---------------------------------------------------------------------------
    # is_sparse
    #---------------------------------------------------------------------------
    def is_sparse(self):
        LGR.debug('DescriptorFile.is_sparse()')
        return ('sparse' in getattr(self, self.K_CREATE_TYPE).lower())
    #---------------------------------------------------------------------------
    # is_esx_disk
    #---------------------------------------------------------------------------
    def is_esx_disk(self):
        LGR.debug('DescriptorFile.is_esx_disk()')
        return ('vmfs' in getattr(self, self.K_CREATE_TYPE).lower())
    #---------------------------------------------------------------------------
    # is_using_physical_disk
    #---------------------------------------------------------------------------
    def is_using_physical_disk(self):
        LGR.debug('DescriptorFile.is_using_physical_disk()')
        return (getattr(self, self.K_CREATE_TYPE) in self.PHY_CREATE_TYPES)
    #---------------------------------------------------------------------------
    # is_using_raw_device_mapping
    #---------------------------------------------------------------------------
    def is_using_raw_device_mapping(self):
        LGR.debug('DescriptorFile.is_using_physical_disk()')
        return (getattr(self, self.K_CREATE_TYPE) in self.RAW_DEV_MAP_CREATE_TYPES)
    #---------------------------------------------------------------------------
    # is_stream_optimized
    #---------------------------------------------------------------------------
    def is_stream_optimized(self):
        LGR.debug('DescriptorFile.is_using_physical_disk()')
        return (getattr(self, self.K_CREATE_TYPE) in self.STREAM_OPTIM_CREATE_TYPES)
    #---------------------------------------------------------------------------
    # parent_filename
    #---------------------------------------------------------------------------
    def parent_filename(self):
        return getattr(self, self.K_PARENT_FILENAME_HINT)
    #---------------------------------------------------------------------------
    # to_str
    #---------------------------------------------------------------------------
    def to_str(self):
        text = '\nDescriptorFile:'
        text += '\n\theader:'
        for key in DescriptorFile.HEADER_KWDS:
            if hasattr(self, key):
                text += '\n\t\t+ {}: {}'.format(key, getattr(self, key))
        text += '\n\textents:'
        for extent in self.extents:
            text += '\n\t\t + {}'.format(extent.to_str())
        text += '\n\tddb:'
        for key, value in self.ddb.items():
            text += '\n\t\t + {}: {}'.format(key, value)
        return text + '\n'
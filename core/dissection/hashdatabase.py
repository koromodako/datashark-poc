#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: hashdatabase.py
#    date: 2017-11-17
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
from utils.config               import config
from utils.helpers.json         import json_load
from utils.helpers.json         import json_dump
from dissection.container       import Container
from utils.helpers.logging      import get_logger
from utils.threading.workerpool import WorkerPool
#===============================================================================
# GLOBALS / CONFIG
#===============================================================================
LGR = get_logger(__name__)
#===============================================================================
# FUNCTIONS
#===============================================================================
#-------------------------------------------------------------------------------
# hashing_routine
#-------------------------------------------------------------------------------
def hashing_routine(fpath):
    LGR.info('processing file: {0}'.format(fpath))
    container = Container(fpath)
    return ([], [(container.sha256, container.path)])
#===============================================================================
# CLASSES
#===============================================================================
#-------------------------------------------------------------------------------
# HashDatabase
#-------------------------------------------------------------------------------
class HashDatabase(object):
    #---------------------------------------------------------------------------
    # __init__
    #---------------------------------------------------------------------------
    def __init__(self, name, fpath):
        self.fpath = fpath
        self.name = name
        self.valid = False
        self.db = self.__load_db()
    #---------------------------------------------------------------------------
    # __load_db
    #---------------------------------------------------------------------------
    def __load_db(self):
        # check if path is valid
        if self.fpath is None and os.path.isfile(self.fpath):
            return {}
        # read database from file
        with open(self.fpath, r) as f:
            dat = json_load(f)
        # set valid and return data
        self.valid = True
        return dat
    #---------------------------------------------------------------------------
    # contains
    #---------------------------------------------------------------------------
    def contains(self, container):
        return (self.valid and self.db.get(container.sha256) is not None)
    #---------------------------------------------------------------------------
    # create
    #   /!\ assumes caller will check input parameters /!\
    #---------------------------------------------------------------------------
    @staticmethod
    def create(path, dirs, recursive, dir_filter, file_filter):
        import os
        # scan for files iterating over directories (recursively if required)
        LGR.info('scanning for files...')
        fpaths = []
        for dpath in dirs:
            adpath = os.path.abspath(dpath)
            if recursive:
                # recursive listing from given directory
                for root, dirs, files in os.walk(adpath):
                    dirs[:] = [ d for d in dirs if dir_filter.keep(d) ]
                    for f in files:
                        if file_filter.keep(f):
                            fpaths.append(os.path.join(root, f))
            else:
                # listing only inside given directory
                for entry in os.listdir(adpath):
                    fpath = os.path.join(adpath, entry)
                    if os.path.isfile(fpath):
                        if file_filter.keep(entry):
                            fpaths.append(fpath)
        LGR.info('start hashing processes...')
        pool = WorkerPool(config('num_workers', default=1))
        results = pool.map(hashing_routine, {}, tasks=fpaths)
        LGR.info('aggregating results...')
        db = {}
        for result in results:
            db[result[0]] = result[1]
        # write database
        with open(path, 'w') as f:
            LGR.info('writing database...')
            json_dump(db, f)
        LGR.info('done.')
    #-----------------------------------------------------------------------
    # merge
    #   /!\ assumes caller will check input parameters /!\
    #-----------------------------------------------------------------------
    @staticmethod
    def merge(fpath, files):
        import os
        # merging files
        LGR.info('merging databases...')
        db = {}
        for f in files:
            with open(f, 'r') as f:
                pdb = json_load(f)
                db.update(pdb)
        # writing output file
        with open(fpath, 'w') as f:
            LGR.info('writing database...')
            json_dump(db, f)
        LGR.info('done.')

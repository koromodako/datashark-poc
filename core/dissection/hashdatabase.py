# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# =============================================================================
# IMPORTS
# =============================================================================
import os
from utils.config import config
from utils.json import json_load
from utils.json import json_dump
from utils.logging import get_logger
from utils.workerpool import WorkerPool
from utils.binary_file import BinaryFile
from utils.action_group import ActionGroup
from dissection.container import Container
# =============================================================================
# GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# FUNCTIONS
# =============================================================================


def hashing_routine(fpath):
    # -------------------------------------------------------------------------
    # hashing_routine
    # -------------------------------------------------------------------------
    LGR.info('processing file: {}'.format(fpath))
    container = Container(fpath, os.path.basename(fpath))
    return ([], [(container.hashed, container.path)])
# =============================================================================
# CLASSES
# =============================================================================


class HashDatabase(object):
    # -------------------------------------------------------------------------
    # HashDatabase
    # -------------------------------------------------------------------------
    def __init__(self, name, fpath):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        self.fpath = fpath
        self.name = name
        self.valid = False
        self.db = self.__load_db()

    def __load_db(self):
        # ---------------------------------------------------------------------
        # __load_db
        # ---------------------------------------------------------------------
        # check if path is valid
        if self.fpath is None or not BinaryFile.exists(self.fpath):
            warn = 'cannot load <{}> hash database, invalid path: {}'.format(
                self.name, self.fpath)
            LGR.warning(warn)
            return {}
        # read database from file
        with open(self.fpath, 'r') as f:
            dat = json_load(f)
        # set valid and return data
        self.valid = True
        return dat

    def contains(self, container):
        # ---------------------------------------------------------------------
        # contains
        # ---------------------------------------------------------------------
        return (self.valid and self.db.get(container.hashed) is not None)

    @staticmethod
    def create(path, dirs, recursive, dir_filter, file_filter):
        # ---------------------------------------------------------------------
        # create
        #   /!\ assumes caller will check input parameters /!\
        # ---------------------------------------------------------------------
        # scan for files iterating over directories (recursively if required)
        LGR.info('scanning for files...')
        fpaths = []
        for dpath in dirs:
            adpath = os.path.abspath(dpath)

            if recursive:
                # recursive listing from given directory
                for root, dirs, files in os.walk(adpath):
                    dirs[:] = [d for d in dirs if dir_filter.keep(d)]
                    for f in files:
                        if file_filter.keep(f):
                            fpaths.append(os.path.join(root, f))
            else:
                # listing only inside given directory
                for entry in os.listdir(adpath):
                    fpath = os.path.join(adpath, entry)
                    if BinaryFile.exists(fpath):
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

    @staticmethod
    def merge(fpath, files):
        # ---------------------------------------------------------------------
        # merge
        #   /!\ assumes caller will check input parameters /!\
        # ---------------------------------------------------------------------
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


class HashDatabaseActionGroup(ActionGroup):
    # -------------------------------------------------------------------------
    # HashDatabaseActionGroup
    # -------------------------------------------------------------------------
    @staticmethod
    def create(keywords, args):
        # ---------------------------------------------------------------------
        # create
        # ---------------------------------------------------------------------
        # check arguments
        if len(args.files) > 1:
            fpath = args.files[0]
            dirs = args.files[1:]
            if os.path.isdir(fpath):
                LGR.error('<{}> is an existing directory.'.format(fpath))
            for dpath in dirs:
                if not os.path.isdir(dpath):
                    LGR.error('<{}> must be an existing directory.'.format(
                        dpath))
            # create database
            HashDatabase.create(fpath, dirs, args.recursive, args.dir_filter,
                                args.file_filter)
        else:
            LGR.warning("this action expect at least these args: output.json "
                        "dir [dir ...]")

    @staticmethod
    def merge(keywords, args):
        # ---------------------------------------------------------------------
        # merge
        # ---------------------------------------------------------------------
        # check arguments
        if len(args.files) < 2:
            LGR.error("this action expect at least these args: output.json "
                      "db.part1.json db.part2.json [... db.partN.json]")
            return

        fpath = args.files[0]
        files = args.files[1:]

        if os.path.isdir(fpath):
            LGR.error('<{}> is an existing directory.'.format(fpath))
            return

        for f in files:
            if not BinaryFile.exists(f):
                LGR.error('<{}> must be an existing file.'.format(f))
                return
        # merge db files
        HashDatabase.merge(fpath, files)

    def __init__(self):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(HashDatabaseActionGroup, self).__init__('hashdb', {
            'create': ActionGroup.action(HashDatabaseActionGroup.create,
                                         'create a hash-database.'),
            'merge': ActionGroup.action(HashDatabaseActionGroup.merge,
                                        'merge given hash-databases')
        })

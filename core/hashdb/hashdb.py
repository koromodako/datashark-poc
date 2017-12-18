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
import utils.fs as fs
import utils.config as config
from utils.wrapper import trace
from utils.logging import get_logger
from utils.wrapper import trace_func
from utils.wrapper import trace_static
from utils.workerpool import WorkerPool
from utils.binary_file import BinaryFile
from utils.action_group import ActionGroup
from container.container import Container
from utils.plugin_importer import PluginImporter
# =============================================================================
# GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# FUNCTIONS
# =============================================================================

@trace_func(__name__)
def hashing_routine(fpath, hashdb):
    # -------------------------------------------------------------------------
    # hashing_routine
    # -------------------------------------------------------------------------
    LGR.info("hashing <{}>...".format(fpath))
    container = Container(fpath, os.path.basename(fpath))

    hashdb.persist(container)
    hashdb.term()

    return ([], [])
# =============================================================================
# CLASSES
# =============================================================================


class HashDB(object):
    ADAPTERS = None
    # -------------------------------------------------------------------------
    # HashDB
    # -------------------------------------------------------------------------
    def __init__(self, conf):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(HashDB, self).__init__()
        self.conf = conf
        self.name = None
        if self.conf is not None:
            self.name = self.conf.get('name')
        self.valid = False
        self.adapter = None
        if HashDB.ADAPTERS is None:
            pi = PluginImporter('hashdb.adapters',
                            __file__, 'adapters',
                            expected_funcs=set(['instance']))

            if not pi.load_plugins():
                LGR.warn("some adapters failed to be loaded.")

            HashDB.ADAPTERS = pi.plugins

    @trace()
    def init(self, mode):
        # ---------------------------------------------------------------------
        # init
        # ---------------------------------------------------------------------
        if self.conf is None:
            LGR.error("hashdb configuration is missing.")
            return False

        if not self.conf.has('adapter'):
            LGR.error("hashdb configuration must have 'adapter' key.")
            return False

        adapter_mod = self.ADAPTERS.get(self.conf.adapter)
        if adapter_mod is None:
            LGR.error("failed to load adapter: <{}>".format(self.conf.adapter))
            return False

        self.adapter = adapter_mod.instance(self.conf.get(self.conf.adapter))
        self.adapter.init(mode)
        if not self.adapter.is_valid():
            LGR.error("invalid adapter instance.")
            return False

        self.valid = True
        return True

    @trace()
    def term(self):
        # ---------------------------------------------------------------------
        # term
        # ---------------------------------------------------------------------
        if self.valid:
            self.adapter.term()
            self.adapter = None
            self.valid = False

    @trace()
    def contains(self, container):
        # ---------------------------------------------------------------------
        # contains
        # ---------------------------------------------------------------------
        if not self.valid:
            return None

        return (self.adapter.lookup(container.hashed) is not None)

    @trace()
    def persist(self, container):
        # ---------------------------------------------------------------------
        # insert
        # ---------------------------------------------------------------------
        if not self.valid:
            return False

        if not self.adapter.insert(container.hashed, container.path):
            return False

        return True

    @trace()
    def merge_into(self, other):
        # ---------------------------------------------------------------------
        # merge
        # ---------------------------------------------------------------------
        if not self.valid or not other.valid:
            return False

        if not self.adapter.merge_into(other.adapter):
            return False

        return True


class HashDBActionGroup(ActionGroup):
    # -------------------------------------------------------------------------
    # HashDBActionGroup
    # -------------------------------------------------------------------------
    @staticmethod
    @trace_static('HashDBActionGroup')
    def adapters(keywords, args):
        hdb = HashDB(None)
        adapters = sorted(HashDB.ADAPTERS.keys())

        text = "\nadapters:"

        if len(adapters) > 0:
            for adapter in adapters:
                text += "\n\t+ {}".format(adapter)
        else:
            text += "\n\tno adapter available."

        text += "\n"
        LGR.info(text)

        return True

    @staticmethod
    @trace_static('HashDBActionGroup')
    def create(keywords, args):
        # ---------------------------------------------------------------------
        # create
        # ---------------------------------------------------------------------
        # check arguments
        if len(args.files) < 2:
            LGR.error("this action expect at least these args: hashdb.conf "
                      "dir [dir ...]")
            return False
        # try to load configuration file
        (hashdb_conf, cf) = config.load_from_file(args.files[0])
        if hashdb_conf is None:
            LGR.error("failed to load hash database configuration.")
            return False
        # check if remaining arguments are directories
        dirs = args.files[1:]
        for dpath in dirs:
            if not os.path.isdir(dpath):
                LGR.error("<{}> must be an existing directory.".format(dpath))
                return False
        # create database
        LGR.info("enumerating files...")
        fpaths = fs.enumerate_files(dirs, args.dir_filter, args.file_filter,
                                    args.recursive)

        LGR.info("connecting to database...")
        hashdb = HashDB(hashdb_conf)
        if not hashdb.init('w'):
            LGR.error("failed to init database.")
            return False

        LGR.info("start hashing processes...")
        pool = WorkerPool(config.value('num_workers', 1))
        kwargs = {
            'hashdb': hashdb
        }
        pool.map(hashing_routine, kwargs, tasks=fpaths)

        LGR.info("done.")
        return True


    @staticmethod
    @trace_static('HashDBActionGroup')
    def merge(keywords, args):
        # ---------------------------------------------------------------------
        # merge
        # ---------------------------------------------------------------------
        # check arguments
        if len(args.files) < 2:
            LGR.error("this action expect at least these args: outdb.conf "
                      "db.0.conf [db.1.conf ... db.N.conf]")
            return False

        odbf = args.files[0]
        (oconf, ocf) = config.load_from_file(odbf)
        odb = HashDB(oconf)
        if not odb.init('w'):
            LGR.error("failed to open <{}> db for writing.".format(odb.name))
            return False

        for f in args.files[1:]:
            (iconf, icf) = config.load_from_file(f)
            idb = HashDB(iconf)
            if not idb.init('r'):
                LGR.warn("failed to open <{}> for reading => "
                            "skipped.".format(idb.name))
                continue
            LGR.info("merging <{}> into <{}>...".format(idb.name, odb.name))
            idb.merge_into(odb)
            idb.term()

        LGR.info("done.")
        odb.term()
        return True

    def __init__(self):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(HashDBActionGroup, self).__init__('hashdb', {
            'adapters': ActionGroup.action(HashDBActionGroup.adapters,
                                           "list hash database adapters."),
            'create': ActionGroup.action(HashDBActionGroup.create,
                                         "create a new hash database."),
            'merge': ActionGroup.action(HashDBActionGroup.merge,
                                        "merge given hash databases.")
        })

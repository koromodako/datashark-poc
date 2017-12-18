# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: sqlite.py
#     date: 2017-12-15
#   author: paul.dautry
#  purpose:
#
#  license:
#    Datashark <progdesc>
#    Copyright (C) 2017 paul.dautry
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
#  IMPORTS
# =============================================================================
import sqlite3
from utils.wrapper import trace
from utils.wrapper import trace_func
from utils.logging import get_logger
from hashdb.hashdb_adapter import HashDBAdapter
# =============================================================================
#  GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
#  CLASSES
# =============================================================================


class SQLiteDB(HashDBAdapter):
    # -------------------------------------------------------------------------
    # SQLiteDB
    # -------------------------------------------------------------------------
    EXPECTED_CONF = {
        'path': "path/to/database.db"
    }

    def __init__(self, conf):
        super(SQLiteDB, self).__init__(conf)

    def _check_conf(self):
        # ---------------------------------------------------------------------
        # _check_conf
        # ---------------------------------------------------------------------
        if self._conf is None:
            return False

        if not self._conf.has('path'):
            LGR.error("missing path in SQLiteDB adapter configuration.")
            return False

        return True

    def insert(self, hexdigest, path):
        self._lock.acquire()

        c = self.conn.cursor()
        c.execute("INSERT INTO hashes VALUES (?, ?)", (hexdigest, path))
        c.close()

        self.conn.commit()

        self._lock.release()
        return True

    def lookup(self, hexdigest):
        self._lock()

        c = self.conn.cursor()
        c.execute("SELECT * FROM hashes WHERE hash=?", (hexdigest))
        record = c.fetchone()
        c.close()

        self._lock.release()
        return record

    def merge_into(self, other):
        self._lock.acquire()

        c = self.conn.cursor()
        c.execute("SELECT * FROM hashes")

        v = c.fetchone()
        while v is not None:
            other.insert(v[0], v[1])
            v = c.fetchone()

        c.close()

        self._lock.release()
        return True

    def _init_r(self):
        try:
            uri = 'file:{}?mode=ro'.format(self._conf.path)
            self.conn = sqlite3.connect(uri, uri=True)
        except Exception as e:
            LGR.exception("failed to init sqlite3 database.")
            return False

        return True

    def _init_w(self):
        try:
            uri = 'file:{}?mode=rwc'.format(self._conf.path)
            self.conn = sqlite3.connect(uri, uri=True)
        except Exception as e:
            LGR.exception("failed to init sqlite3 database.")
            return False

        c = self.conn.cursor()
        c.execute("DROP INDEX IF EXISTS hashes_idx")
        c.execute("DROP TABLE IF EXISTS hashes")
        c.execute("CREATE TABLE hashes(hash, abspath)")
        c.execute("CREATE INDEX hashes_idx ON hashes(hash)")
        c.close()
        self.conn.commit()

        return True

    def _term_r(self):
        self.conn.close()

    def _term_w(self):
        self.conn.close()

# =============================================================================
#  FUNCTIONS
# =============================================================================


@trace_func(__name__)
def instance(conf):
    return SQLiteDB(conf)

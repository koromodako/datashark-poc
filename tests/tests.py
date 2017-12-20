#!/usr/bin/env python3
# -!- encoding:utf8 -!-
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     file: tests.py
#     date: 2017-12-17
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
from os import makedirs
from shutil import which
from subprocess import getstatusoutput
from termcolor import colored, cprint
# =============================================================================
#  CLASSES
# =============================================================================


def stub():
    # -------------------------------------------------------------------------
    # stub
    # -------------------------------------------------------------------------
    return True


class Test(object):
    # -------------------------------------------------------------------------
    # Test
    # -------------------------------------------------------------------------

    @staticmethod
    def exec_cmd(cmd, expect_code=0):
        # ---------------------------------------------------------------------
        # exec_cmd
        # ---------------------------------------------------------------------
        (exit_code, output) = getstatusoutput(' '.join(cmd))
        return (exit_code == expect_code, exit_code, output)

    def __init__(self, name, cmd, init=stub, term=stub, expect_code=0):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(Test, self).__init__()
        self.name = name
        self.cmd = cmd
        self.init = init
        self.term = term
        self.expect_code = expect_code

    def run(self):
        # ---------------------------------------------------------------------
        # run
        # ---------------------------------------------------------------------
        if not self.init():
            return (False, None, "init() failed.")
        (exit_ok, exit_code, output) = self.exec_cmd(self.cmd,
                                                     self.expect_code)
        self.term()
        return (exit_ok, exit_code, output)

# =============================================================================
#  FUNCTIONS
# =============================================================================


def pout(msg):
    # -------------------------------------------------------------------------
    # pout
    # -------------------------------------------------------------------------
    cprint(msg, 'magenta')


def run_tests(tests):
    # -------------------------------------------------------------------------
    # run_tests
    # -------------------------------------------------------------------------
    makedirs('tmp', exist_ok=True)
    makedirs('logs', exist_ok=True)
    failure = colored("FAILURE", 'red')
    success = colored("SUCCESS", 'green')
    success_ctr = 0
    failure_ctr = 0

    pout((">" * 30) + " RUNNING TESTS " + ("<" * 30))
    for test in tests:
        exit_ok, exit_code, output = test.run()

        if exit_ok:
            status = success
            success_ctr += 1
        else:
            status = failure
            failure_ctr += 1

        warn = ""
        if exit_code is None:
            warn = colored(" /!\\ {}".format(output), 'yellow')

        print("{}: {} (code={}){}".format(test.name, status, exit_code, warn))

        with open('logs/{}.log'.format(test.name), 'w') as f:
            f.write(output)

    pout((">" * 30) + " TESTING REPORT " + ("<" * 30))
    pout("count:")
    pout("\t{}: {}".format(failure, failure_ctr))
    pout("\t{}: {}".format(success, success_ctr))
    pout("\ttotal: {}".format(failure_ctr + success_ctr))

# =============================================================================
#  GLOBALS
# ============================================================================
DATA_DIR = 'data/'
SUBDIR_DIR = '{}subdir'.format(DATA_DIR)
RENZIK_JPG = '{}renzik_sm.jpg'.format(DATA_DIR)
# =============================================================================
# TEST FUNCTIONS
# =============================================================================
def hashdb_merge_init():
    # -------------------------------------------------------------------------
    # hashdb_merge_init
    # -------------------------------------------------------------------------
    (exit_ok, _, output) = Test.exec_cmd(['datashark', 'hashdb.create',
                                      'config/bhdb-1.conf', DATA_DIR])
    if not exit_ok:
        return False

    (exit_ok, _, output) = Test.exec_cmd(['datashark', 'hashdb.create',
                                      'config/bhdb-2.conf', SUBDIR_DIR])
    if not exit_ok:
        return False

    return True
# =============================================================================
# TESTS ARRAY
# =============================================================================
TESTS = [
    # -------------------------------------------------------------------------
    #  GENERIC
    # -------------------------------------------------------------------------
    Test("help", ['datashark', 'help']),
    # -------------------------------------------------------------------------
    #  HASHDB
    # -------------------------------------------------------------------------
    Test("hashdb.help",
         ['datashark', 'hashdb.help']),
    Test("hashdb.adapters",
         ['datashark', 'hashdb.adapters']),
    Test("hashdb.create",
         ['datashark', 'hashdb.create', 'config/whdb.conf', DATA_DIR]),
    Test("hashdb.merge",
         ['datashark', 'hashdb.merge',
          'config/bhdb.conf', 'config/bhdb-1.conf', 'config/bhdb-2.conf'],
          init=hashdb_merge_init),
    # -------------------------------------------------------------------------
    #  CONTAINER
    # -------------------------------------------------------------------------
    Test("container.help",
         ['datashark', 'container.help']),
    Test("container.hash",
         ['datashark', 'container.hash', RENZIK_JPG]),
    Test("container.mimes",
         ['datashark', 'container.mimes', RENZIK_JPG]),
    # -------------------------------------------------------------------------
    #  DISSECTION
    # -------------------------------------------------------------------------
    Test("dissection.help",
         ['datashark', 'dissection.help']),
    Test("dissection.carvers",
         ['datashark', 'dissection.carvers']),
    Test("dissection.dissectors",
         ['datashark', 'dissection.dissectors']),
    Test("dissection.dissect",
         ['datashark',
          '--dissection-config=config/dissection.conf',
          'dissection.dissect', RENZIK_JPG]),
    # -------------------------------------------------------------------------
    #  DISSECTIONDB
    # -------------------------------------------------------------------------
    Test("dissectiondb.help",
         ['datashark', 'dissectiondb.help']),
    Test("dissectiondb.adapters",
         ['datashark', 'dissectiondb.adapters']),
    # -------------------------------------------------------------------------
    #  WOKSPACE
    # -------------------------------------------------------------------------
    Test("workspace.help",
         ['datashark', 'workspace.help']),
    Test("workspace.list",
         ['datashark', 'workspace.list']),
    Test("workspace.clean",
         ['datashark', 'workspace.clean'])
]
# =============================================================================
#  SCRIPT
# =============================================================================
if __name__ == '__main__':

    if which('datashark') is None:
        print("datashark command is missing... cannot proceed to testing...")
        exit(1)

    run_tests(TESTS)
    exit(0)

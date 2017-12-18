# -----------------------------------------------------------------------------
#    file: config.py
#    date: 2017-11-12
#  author: paul.dautry
# purpose:
#    Utils program configuration
# license:
#    Utils
#    Copyright (C) 2017  Paul Dautry
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------
# IMPORTS
# =============================================================================
import os
from argparse import ArgumentParser
from utils.json import json_load
from utils.logging import get_logger
from utils.wrapper import trace_func
from utils.configobj import ConfigObj
from utils.constants import PROG_NAME
from utils.constants import PROG_VERSION
from utils.constants import LICENSE
from utils.constants import LICENSE_WARRANTY
from utils.constants import LICENSE_CONDITIONS
# =============================================================================
# CONFIGURATION
# =============================================================================
LGR = get_logger(__name__)
ARGS = None     # do not edit this value
CONFIG = None   # do not edit this value
# =============================================================================
# FUNCTIONS
# =============================================================================


@trace_func(__name__)
def prog_prompt(lvl):
    # -------------------------------------------------------------------------
    # prog_prompt
    #
    # -------------------------------------------------------------------------
    return '({})[{}]> '.format(PROG_NAME, lvl)


@trace_func(__name__)
def get_arg_parser():
    # -------------------------------------------------------------------------
    # get_arg_parser
    #
    # -------------------------------------------------------------------------
    parser = ArgumentParser()
    parser.add_argument('--version',
                        action='store_true',
                        help="Show program version.")
    parser.add_argument('-w', '--warranty',
                        action='store_true',
                        help="Prints license warranty then exits.")
    parser.add_argument('-c', '--conditions',
                        action='store_true',
                        help="Prints license conditions then exits.")
    parser.add_argument('-s', '--silent',
                        action='store_true',
                        help="Do not output anything. A log will be produced "
                        "anyway.")
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help="Increase program verbosity.")
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help="Start in debug mode.")
    return parser


@trace_func(__name__)
def print_version():
    # -------------------------------------------------------------------------
    # print_license
    #
    # -------------------------------------------------------------------------
    print(PROG_VERSION)


@trace_func(__name__)
def print_license():
    # -------------------------------------------------------------------------
    # print_license
    #
    # -------------------------------------------------------------------------
    print(LICENSE)


@trace_func(__name__)
def print_license_warranty():
    # -------------------------------------------------------------------------
    # print_license_warranty
    #
    # -------------------------------------------------------------------------
    print(LICENSE_WARRANTY)


@trace_func(__name__)
def print_license_conditions():
    # -------------------------------------------------------------------------
    # print_license_conditions
    #
    # -------------------------------------------------------------------------
    print(LICENSE_CONDITIONS)


@trace_func(__name__)
def load_from_file(path):
    # -------------------------------------------------------------------------
    # load_from_file
    # -------------------------------------------------------------------------
    if path.startswith('~'):
        path = os.path.expanduser(path)

    if not os.path.isfile(path):
        LGR.warn("invalid path <{}> => skipped.".format(path))
        return (None, None)

    with open(path, 'r') as f:
        try:
            config = ConfigObj(json_load(f))
            return (config, path)
        except Exception as e:
            LGR.exception("failed while loading <{}>".format(path))

    return (None, None)


@trace_func(__name__)
def load():
    # -------------------------------------------------------------------------
    # load
    #
    # -------------------------------------------------------------------------
    global CONFIG

    conf_fname = '{}.conf'.format(PROG_NAME)
    conf_path = os.path.join(PROG_NAME, conf_fname)
    config_files = [
        conf_fname,
        '~/.config/{}'.format(conf_path),
        '/etc/{}'.format(conf_path)
    ]

    for f in config_files:
        (CONFIG, path) = load_from_file(f)
        if CONFIG is not None:
            LGR.info("configuration loaded from <{}>".format(f))
            return True

    return False


@trace_func(__name__)
def set_args(args):
    # -------------------------------------------------------------------------
    # set_args
    # -------------------------------------------------------------------------
    global ARGS
    ARGS = args


@trace_func(__name__)
def value(option, default=None):
    # -------------------------------------------------------------------------
    # value
    #   \brief returns application configuration value
    # -------------------------------------------------------------------------
    # read option following priority order
    # 1 - try command line option
    if ARGS is not None and option in dir(ARGS):
        val = getattr(ARGS, option, None)
        if val is not None:
            LGR.debug("config_args['{}'] -> {}".format(option, val))
            return val
    # 2 - try configuration file option
    if CONFIG is not None:
        val = CONFIG.get(option, None)
        if val is not None:
            LGR.debug("config_file['{}'] -> {}".format(option, val))
            return val
    # 3 - finally return default argument
    LGR.debug("config_dflt['{}'] -> {}".format(option, default))
    return default


@trace_func(__name__)
def load_from_value(option):
    # -------------------------------------------------------------------------
    # load_from_value
    # -------------------------------------------------------------------------
    f = value(option)
    if f is None:
        return None

    (config, path) = load_from_file(f)

    return config

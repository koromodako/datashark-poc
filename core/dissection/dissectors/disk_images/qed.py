# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: qed.py
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
from utils.logging import todo
from utils.logging import get_logger
from utils.wrapper import trace_func
from utils.action_group import ActionGroup
from container.container import Container
# =============================================================================
# GLOBALS / CONFIG
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# FUNCTIONS
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
    todo(LGR, 'implement qed.can_dissect(),'
         'for now will always return False.',
         no_raise=True)
    return False
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
    raise NotImplementedError
    return []
##
## @brief      { function_description }
## @warning    public mandatory function that the module must define
##
## @return     { description_of_the_return_value }
##
@trace_func(__name__)
def action_group():
    return ActionGroup('qed', {})

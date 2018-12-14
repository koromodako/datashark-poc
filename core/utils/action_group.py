# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: action_group.py
#    date: 2017-11-20
#  author: koromodako
# purpose:
#
# license:
#   Datashark <progdesc>
#   Copyright (C) 2017 koromodako
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
from textwrap import wrap
from utils.wrapper import trace
from utils.logging import get_logger
from utils.wrapper import trace_static
from utils.constants import TAB
# =============================================================================
# GLOBALS
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# CLASSES
# =============================================================================
##
## @brief      Class for action group.
##
class ActionGroup(object):
    ##
    ## { item_description }
    ##
    SEP = '.'
    ##
    ## { item_description }
    ##
    K_HELP = 'help'
    ##
    ## { item_description }
    ##
    K_FUNC = 'func'
    ##
    ## @brief      Constructs the object.
    ##
    ## @param      name     The name
    ## @param      actions  The actions
    ##
    def __init__(self, name, actions):
        super(ActionGroup, self).__init__()
        self.name = name
        self.actions = actions
        self.actions['help'] = ActionGroup.action(self.help, "prints help.")
    ##
    ## @brief      { function_description }
    ##
    ## @param      func  The function
    ## @param      help  The help
    ##
    ## @return     { description_of_the_return_value }
    ##
    @staticmethod
    @trace_static('ActionGroup')
    def action(func, help=''):
        return {
            ActionGroup.K_FUNC: func,
            ActionGroup.K_HELP: help
        }
    ##
    ## @brief      { function_description }
    ##
    ## @param      keywords  The keywords
    ## @param      args      The arguments
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def perform_action(self, keywords, args=[]):
        action = self.actions.get(keywords[0], None)

        if action is None:
            LGR.error("unknown action.")
            return False

        subkeywords = keywords[1:]

        if isinstance(action, ActionGroup):

            if len(subkeywords) == 0:
                LGR.error("missing keyword after "
                          "<{}>.".format(keywords[0]))
                return False

            return action.perform_action(subkeywords, args)

        return action[ActionGroup.K_FUNC](subkeywords, args)
    ##
    ## @brief      Determines if it has action.
    ##
    ## @param      keywords  The keywords
    ##
    ## @return     True if has action, False otherwise.
    ##
    @trace()
    def has_action(self, keywords):
        return (self.actions.get(keywords[0], None) is not None)
    ##
    ## @brief      { function_description }
    ##
    ## @param      keywords  The keywords
    ## @param      args      The arguments
    ## @param      depth     The depth
    ##
    ## @return     { description_of_the_return_value }
    ##
    @trace()
    def help(self, keywords, args, depth=0):
        help_txt = ""
        for keyword, action in self.actions.items():
            help_txt += "\n{}{}:".format(ActionGroup.SEP if depth > 0 else "",
                                         keyword)
            if isinstance(action, ActionGroup):
                subhelp_txt = action.help(keywords, args, depth+1)
                help_txt += subhelp_txt.replace("\n", "\n{}".format(TAB))
                continue

            for line in wrap(action[ActionGroup.K_HELP], width=50):
                help_txt += "\n{}{}".format(TAB, line)

        if depth > 0:
            return help_txt

        sep = "-" * (len(self.name) + 7)
        ptxt = "\n{sep} HELP {name} {sep}".format(sep=sep, name=self.name)
        ptxt += help_txt
        ptxt += "\n{sep}{sep}{sep}".format(sep=sep)
        print(ptxt)
        return True

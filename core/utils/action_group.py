# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: action_group.py
#    date: 2017-11-20
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
from utils.logging import get_logger
# =============================================================================
# GLOBALS
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# CLASSES
# =============================================================================


class ActionGroup(object):
    # -------------------------------------------------------------------------
    # ActionGroup
    # -------------------------------------------------------------------------
    SEP = '.'
    K_HELP = 'help'
    K_FUNC = 'func'

    def __init__(self, name, actions):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        self.name = name
        self.actions = actions
        self.actions['help'] = ActionGroup.action(self.help, 'prints help.')

    @staticmethod
    def action(func, help=''):
        # ---------------------------------------------------------------------
        # action
        # ---------------------------------------------------------------------
        LGR.debug('ActionGroup.action()')
        return {
            ActionGroup.K_FUNC: func,
            ActionGroup.K_HELP: help
        }

    def perform_action(self, keywords, args=[]):
        # ---------------------------------------------------------------------
        # perform_action
        # ---------------------------------------------------------------------
        LGR.debug('ActionGroup.perform_action()')
        action = self.actions.get(keywords[0], None)
        if action is None:
            LGR.error('unknown action.')
        else:
            subkeywords = keywords[1:]
            if isinstance(action, ActionGroup):
                if len(subkeywords) == 0:
                    LGR.error("missing keyword after "
                              "<{}>.".format(keywords[0]))
                    return
                action.perform_action(subkeywords, args)
            else:
                action[ActionGroup.K_FUNC](subkeywords, args)

    def has_action(self, keywords):
        # ---------------------------------------------------------------------
        # has_action
        # ---------------------------------------------------------------------
        LGR.debug('ActionGroup.has_action()')
        return (self.actions.get(keywords[0], None) is not None)

    def help(self, keywords, args, depth=0):
        # ---------------------------------------------------------------------
        # help
        # ---------------------------------------------------------------------
        LGR.debug('ActionGroup.help()')
        help_txt = ''
        for keyword, action in self.actions.items():
            help_txt += '\n{}{}:'.format(ActionGroup.SEP if depth > 0 else '',
                                         keyword)
            if isinstance(action, ActionGroup):
                help_txt += action.help(keywords, args, depth+1)
                help_txt = help_txt.replace('\n', '\n\t')
            else:
                help_txt += ' ' + action[ActionGroup.K_HELP]
        if depth > 0:
            return help_txt
        else:
            sep = '-' * (len(self.name) + 7)
            ptxt = '\n{sep} HELP {name} {sep}'.format(sep=sep, name=self.name)
            ptxt += help_txt
            ptxt += '\n{sep}{sep}{sep}'.format(sep=sep)
            LGR.info(ptxt)

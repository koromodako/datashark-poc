# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#    file: cli.py
#    date: 2017-07-23
#  author: paul.dautry
# purpose:
#    Utils CLI-related functions
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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# =============================================================================
from shutil import which
from subprocess import call
from subprocess import Popen
from subprocess import PIPE
from utils.config import prog_prompt
from utils.logging import get_logger
# =============================================================================
# GLOBAL
# =============================================================================
LGR = get_logger(__name__)
# =============================================================================
# CLASSES
# =============================================================================


class CLI(object):
    # -------------------------------------------------------------------------
    # CLI
    # -------------------------------------------------------------------------
    @staticmethod
    def read_input(prompt, allow_empty=False, expect_digit=False):
        # ---------------------------------------------------------------------
        # read_input
        # ---------------------------------------------------------------------
        LGR.debug('CLI.read_input(<%s>, allow_empty=%s, expect_digit=%s)' % (
            prompt, allow_empty, expect_digit))
        uinput = ''
        if not isinstance(prompt, str):
            LGR.error('read_input prompt argument must be a string. (dev)')
        full_prompt = prog_prompt('?') + prompt
        uinput = input(full_prompt)
        while not allow_empty and len(uinput) == 0:
            LGR.error('empty answer is not allowed.')
            uinput = input(full_prompt)
        while expect_digit and not uinput.isdigit():
            LGR.error('answer must be a digit.')
            uinput = input(full_prompt)
        if expect_digit:
            uinput = int(uinput, 10)
        return uinput

    @staticmethod
    def read_input_loop(prompt, subprompt, expect_digit=False):
        # ---------------------------------------------------------------------
        # read_input_loop
        # ---------------------------------------------------------------------
        LGR.debug('CLI.read_input_loop(<%s>, <%s>, expect_digit=%s)' % (
            prompt, subprompt, expect_digit))
        out = []
        print(prog_prompt('?') + prompt)
        uinput = CLI.read_input(subprompt, True, expect_digit)
        while uinput != '.' and len(uinput) > 0:
            out.append(uinput)
            uinput = CLI.read_input(subprompt, False, expect_digit)
        return out

    @staticmethod
    def confirm(question):
        # ---------------------------------------------------------------------
        # confirm
        # ---------------------------------------------------------------------
        LGR.debug('CLI.confirm(<%s>)' % question)
        resp = CLI.read_input('%s [y/*]: ' % question)
        return (resp == 'y')

    @staticmethod
    def choose_one(prompt, among):
        # ---------------------------------------------------------------------
        # choose_one
        # ---------------------------------------------------------------------
        LGR.debug('CLI.choose_one(<%s>,among=%s)' % (prompt, among))
        if not isinstance(among, list) or len(among) < 2:
            raise ValueError('among must be a list with at least 2 elements.')
        print(prog_prompt('?') + prompt)
        for i in range(len(among)):
            print('\t%02d: %s' % (i, among[i]))
        uinput = CLI.read_input('select a number: ', expect_digit=True)
        while uinput < 0 or uinput >= len(among):
            LGR.error('input must be in [0,%d]' % (len(among)-1))
            uinput = CLI.read_input('select a number: ', expect_digit=True)
        return among[uinput]

    @staticmethod
    def look_for_commands(commands):
        # ---------------------------------------------------------------------
        # look_for_commands
        # ---------------------------------------------------------------------
        LGR.debug('CLI.look_for_commands(%s)' % commands)
        if not isinstance(commands, list):
            raise ValueError('CLI.look_for_commands expects "commands" to be '
                             'a list.')
        for cmd in commands:
            if which(cmd) is None:
                LGR.error('"{}" command seems to be unavailable.'.format(cmd))
                return False
        return True

    @staticmethod
    def exec(args):
        # ---------------------------------------------------------------------
        # exec
        # ---------------------------------------------------------------------
        LGR.debug('CLI.exec()')
        LGR.info('exec cmd: {}'.format(' '.join(args)))
        call(args)

    @staticmethod
    def exec_shell(cmd):
        # ---------------------------------------------------------------------
        # exec_shell
        # ---------------------------------------------------------------------
        LGR.debug('CLI.exec()')
        LGR.info('exec cmd: {}'.format(cmd))
        call(cmd, shell=True)

    @staticmethod
    def start_proc(args, wait=True, capture_outputs=False, cwd=None):
        # ---------------------------------------------------------------------
        # start_proc
        # ---------------------------------------------------------------------
        LGR.debug('CLI.start_proc()')
        LGR.info('start process with: {}'.format(' '.join(args)))
        kwargs = {}
        if cwd is not None:
            kwargs['cwd'] = cwd
        if capture_outputs:
            kwargs['stdout'] = PIPE
            kwargs['stderr'] = PIPE
        p = Popen(args, **kwargs)
        if wait:
            p.wait()
        return p


class RePrinter(object):
    # -------------------------------------------------------------------------
    # RePrinter
    # -------------------------------------------------------------------------
    CR = '\r'
    BLANK = ' '

    def __init__(self):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(RePrinter, self).__init__()
        self.__prev_sz = 0

    def __erase(self):
        # ---------------------------------------------------------------------
        # __erase
        # ---------------------------------------------------------------------
        print(self.__prev_sz * self.BLANK, end=self.CR)

    def print(self, line):
        # ---------------------------------------------------------------------
        # print
        # ---------------------------------------------------------------------
        self.__erase()
        self.__prev_sz = len(line)
        print(line, end=self.CR)

    def finish(self, text=''):
        # ---------------------------------------------------------------------
        # finish
        # ---------------------------------------------------------------------
        self.__prev_sz = 0
        print(text)


class CLIProgressBar(RePrinter):
    # -------------------------------------------------------------------------
    # CLIProgressBar
    #
    # USAGE:
    #
    # import time
    # from utils.cli import CLIProgressBar
    #
    # if __name__ == '__main__':
    #     bar = CLIProgressBar(show_exact=True)
    #     total = 100
    #     bar.init(total)
    #     for i in range(total):
    #         j = i+1
    #         bar.update(j, 'even' if (j % 2 == 0) else 'odd')
    #         time.sleep(0.5)
    #     bar.done()
    # -------------------------------------------------------------------------
    def __init__(self, show_percentage=True, show_exact=False,
                 bar_chars=('[', '>', '=', ']')):
        # ---------------------------------------------------------------------
        # __init__
        # ---------------------------------------------------------------------
        super(CLIProgressBar, self).__init__()
        self.show_percentage = show_percentage
        self.show_exact = show_exact
        self.total = 100.0
        if len(bar_chars) != 4:
            raise ValueError('bar_chars is expected to be a 4 chars tuple')
        self.begin = bar_chars[0]
        self.halfcell = bar_chars[1]
        self.fullcell = bar_chars[2]
        self.end = bar_chars[3]
        self.prev_bar = ''

    def __floatify(self, value):
        # ---------------------------------------------------------------------
        # __floatify
        # ---------------------------------------------------------------------
        if isinstance(value, int):
            return float(value)
        return value

    def init(self, total):
        # ---------------------------------------------------------------------
        # init
        # ---------------------------------------------------------------------
        total = self.__floatify(total)
        if not isinstance(total, float) or total < 0.0:
            raise ValueError('total must be in [0.0, +inf[')
        self.total = total
        return True

    def update(self, value, text=''):
        # ---------------------------------------------------------------------
        # update
        # ---------------------------------------------------------------------
        value = self.__floatify(value)
        if not isinstance(value, float) or value < 0.0 or value > self.total:
            raise ValueError('value must be a float in [0.0, '
                             '{}]'.format(self.total))

        perc = (value / self.total) * 100

        percentage = ''
        if self.show_percentage:
            percentage = ' {:5.1f}%'.format(perc)

        exact = ''
        if self.show_exact:
            exact = ' {:.1f}/{:.1f}'.format(value, self.total)

        q = int(perc) // 2
        r = int(perc) % 2

        bar = '{}{}{}{}{}'.format(self.begin,
                                  self.fullcell * q,
                                  self.halfcell * r,
                                  RePrinter.BLANK * (50 - (q + r)),
                                  self.end)

        self.prev_bar = '{}{}{} {}'.format(bar, percentage, exact, text)
        self.print(self.prev_bar)

    def done(self):
        # ---------------------------------------------------------------------
        # done
        # ---------------------------------------------------------------------
        self.total = 100.0
        self.finish(self.prev_bar)

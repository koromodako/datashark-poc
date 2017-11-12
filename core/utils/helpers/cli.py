#!/usr/bin/env python3
# -!- encoding:utf8 -!-
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
#===============================================================================
from shutil                 import which
from subprocess             import call
from subprocess             import Popen
from subprocess             import PIPE
from utils.config           import prog_prompt
from utils.helpers.logging  import get_logger
#===============================================================================
# GLOBAL
#===============================================================================
lgr = get_logger(__name__)
#===============================================================================
# CLASS
#===============================================================================
class CLI(object):
    #---------------------------------------------------------------------------
    # read_input
    #---------------------------------------------------------------------------
    @staticmethod
    def read_input(prompt, allow_empty=False, expect_digit=False):
        lgr.debug('CLI.read_input(<%s>, allow_empty=%s, expect_digit=%s)' % (
            prompt, allow_empty, expect_digit))
        uinput = ''
        if not isinstance(prompt, str):
            lgr.error('read_input prompt argument must be a string. (dev)')
        full_prompt = prog_prompt('?') + prompt
        uinput = input(full_prompt)
        while not allow_empty and len(uinput) == 0:
            lgr.error('empty answer is not allowed.')
            uinput = input(full_prompt)
        while expect_digit and not uinput.isdigit():
            lgr.error('answer must be a digit.')
            uinput = input(full_prompt)
        if expect_digit:
            uinput = int(uinput, 10)
        return uinput
    #---------------------------------------------------------------------------
    # read_input_loop
    #---------------------------------------------------------------------------
    @staticmethod
    def read_input_loop(prompt, subprompt, expect_digit=False):
        lgr.debug('CLI.read_input_loop(<%s>, <%s>, expect_digit=%s)' % (
            prompt, subprompt, expect_digit))
        out = []
        print(prog_prompt('?') + prompt)
        uinput = CLI.read_input(subprompt, True, expect_digit)
        while uinput != '.' and len(uinput) > 0:
            out.append(uinput)
            uinput = CLI.read_input(subprompt, False, expect_digit)
        return out
    #---------------------------------------------------------------------------
    # confirm
    #---------------------------------------------------------------------------
    @staticmethod
    def confirm(question):
        lgr.debug('CLI.confirm(<%s>)' % question)
        resp = CLI.read_input('%s [y/*]: ' % question)
        return (resp == 'y')
    #---------------------------------------------------------------------------
    # choose_one
    #---------------------------------------------------------------------------
    @staticmethod
    def choose_one(prompt, among):
        lgr.debug('CLI.choose_one(<%s>,among=%s)' % (prompt, among))
        if not isinstance(among, list) or len(among) < 2:
            raise ValueError('among must be a list with at least 2 elements.')
        print(prog_prompt('?') + prompt)
        for i in range(len(among)):
            print('\t%02d: %s' % (i, among[i]))
        uinput = CLI.read_input('select a number: ', expect_digit=True)
        while uinput < 0 or uinput >= len(among):
            lgr.error('input must be in [0,%d]' % (len(among)-1))
            uinput = CLI.read_input('select a number: ', expect_digit=True)
        return among[uinput]
    #---------------------------------------------------------------------------
    # look_for_commands
    #---------------------------------------------------------------------------
    @staticmethod
    def look_for_commands(commands):
        lgr.debug('CLI.look_for_commands(%s)' % commands)
        if not isinstance(commands, list):
            raise ValueError('CLI.look_for_commands expects "commands" to be a list.')
        for cmd in commands:
            if which(cmd) is None:
                lgr.error('"{0}" command seems to be unavailable.'.format(cmd))
                return False
        return True
    #---------------------------------------------------------------------------
    # exec
    #---------------------------------------------------------------------------
    @staticmethod
    def exec(args):
        lgr.debug('CLI.exec()')
        lgr.info('exec cmd: {0}'.format(' '.join(args)))
        call(args)
    #---------------------------------------------------------------------------
    # exec_shell
    #---------------------------------------------------------------------------
    @staticmethod
    def exec_shell(cmd):
        lgr.debug('CLI.exec()')
        lgr.info('exec cmd: {0}'.format(cmd))
        call(cmd, shell=True)
    #---------------------------------------------------------------------------
    # start_proc
    #---------------------------------------------------------------------------
    @staticmethod
    def start_proc(args, wait=True, capture_outputs=False, cwd=None):
        lgr.debug('CLI.start_proc()')
        lgr.info('start process with: {0}'.format(' '.join(args)))
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

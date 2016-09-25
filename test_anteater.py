# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from subprocess import check_output


def test_echo():
    '''An example test.'''
    result = run_cmd("echo hello world")
    assert result == "hello world\n"


def run_cmd(cmd):
    '''Run a shell command `cmd` and return its output.'''
    return check_output(cmd, shell=True).decode('utf-8')

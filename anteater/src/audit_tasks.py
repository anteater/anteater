#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys

# terminal colors
START = "\x1b["
GREEN = "32m"
RED = "31m"
YELLOW = "33m"
BLUE = "34m"
PURPLE = "35m"
BOLD = "01;"
UNDERLINE = "04;"
RESET = "\x1b[00m"

BOLDGRN = START + BOLD + GREEN
BOLDRED = START + BOLD + RED
UNKNOWN = START + BOLD + YELLOW
TITLE = START + BOLD + PURPLE
MESSAGE = START + BOLD + BLUE


def audit_all(project):
    for project in projects:
        audit_project(project)


def audit_project(reports_dir, project):
    projdir = 'repos/{0}'.format(project)
    pyimps = []
    javaimp = []
    cinclude = []
    py = 0
    sh = 0
    java = 0
    c = 0
    for dirname, dirnames, filenames in os.walk(projdir):
        for filename in filenames:
            # check if python file
            if filename.endswith('.py'):
                # Lets count it
                py = py + 1
                # Open the file to gather modules into pyimp list
                with open(os.path.join(dirname.rstrip(), filename)) as f:
                    for line in f.readlines():
                        # Regex match for import (e.g. import subprocess)
                        match = re.search(r'import (\w+)', line)
                        if match:
                            # Append each module to the pyimps list
                            pyimps.append(match.group(1))
            elif filename.endswith('.sh'):
                # Count shell scripts
                sh = sh + 1
            elif filename.endswith('.java'):
                java = java + 1
                with open(os.path.join(dirname.rstrip(), filename)) as f:
                    for line in f.readlines():
                        if 'import' in line:
                            line = line.split()
                            try:
                                javaimp.append(line[1])
                            except IndexError:
                                pass
            elif filename.endswith('.c'):
                c = c + 1
                with open(os.path.join(dirname.rstrip(), filename)) as f:
                    for line in f.readlines():
                        if '#include' in line:
                            line = line.split()
                            try:
                                cinclude.append(line[1])
                            except IndexError:
                                pass
    if py > 1:
        # Report the amount of Python Scrips found using the 'py counter'
        sys.stdout.write("%s%s python files found.%s" % (MESSAGE, py, RESET))
        sys.stdout.write("\n\n")
        # Print out the import modules found, in a nicer format then a long
        # python list
        sys.stdout.write("%sPython modules Imported:%s" % (MESSAGE, RESET))
        sys.stdout.write("\n")
        # Remove duplicates
        pyimps = list(set(pyimps))
        print('\n'.join('{}: {}'.format(*k) for k in enumerate(pyimps)))
        print '\n'
    if sh > 1:
        print '{0} shellscript files found\n'.format(sh)
    if java > 1:
        sys.stdout.write("%s%s java files found.%s" % (MESSAGE, java, RESET))
        sys.stdout.write("\n\n")
        sys.stdout.write("%sJava modules Imported:%s" % (MESSAGE, RESET))
        sys.stdout.write("\n")
        # Remove duplicates
        javaimp = list(set(javaimp))
        print('\n'.join('{}: {}'.format(*k) for k in enumerate(javaimp)))
    if c > 1:
        sys.stdout.write("%s%s C files found.%s" % (MESSAGE, c, RESET))
        sys.stdout.write("\n\n")
        # Remove duplicates
        sys.stdout.write("%sC libraries Imported:%s" % (MESSAGE, RESET))
        sys.stdout.write("\n")
        cinclude = list(set(cinclude))
        print('\n'.join('{}: {}'.format(*k) for k in enumerate(cinclude)))
    if py < 1 and sh < 1 and java < 1 and c < 1:
        print "No code found for this project\n"

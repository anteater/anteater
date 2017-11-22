##############################################################################
# Copyright (c) 2017 Luke Hinds <lhinds@redhat.com>, Red Hat
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0
##############################################################################

# python generate-sha256.py --project /home/user/opnfv/infra
# output made to working directory, file `output.yaml`

import os
import sys
import hashlib
import argparse
from binaryornot.check import is_binary

hasher = hashlib.sha256()
parser = argparse.ArgumentParser()

parser.add_argument('--project', help="Full path to project folder",
                    required=True)
args = parser.parse_args()
ignore_dirs = ['.git']
sys.stdout = open('output.yaml', 'w')

print("binaries:")
for root, dirs, files in os.walk(args.project):
    dirs[:] = [d for d in dirs if d not in ignore_dirs]
    for file in files:
        full_path = os.path.join(root, file)
        if is_binary(full_path):
            with open(full_path, 'rb') as afile:
                buf = afile.read()
                hasher.update(buf)
                split_path = full_path.split(args.project + '/', 1)[-1]
                print("  {}:".format(split_path))
                sum = hasher.hexdigest()
                print("    - {}".format(sum))
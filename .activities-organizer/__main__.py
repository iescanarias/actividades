#!/usr/bin/env python3

import sys
import os
from package import process_activity

# get script name
script = sys.argv[0]

# get script arguments
args = sys.argv[1:]

# check arguments
if len(args) != 1:
    print(f'usage: python {script} <activity path>')
    sys.exit(1)

# get activity path from arguments
activity_path = args[0]

# create README.md file for activity
process_activity.create_readme(activity_path)
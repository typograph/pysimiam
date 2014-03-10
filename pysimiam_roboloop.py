#!/usr/bin/env python
# QtSimiam main executable
# Author: Tim Fuchs <typograph@elec.ru>
# Description: This is the top-level application for QtSimiam for controlling real robots.

import sys
sys.path.insert(0, './scripts')
from roboloop import RoboLoop
import helpers

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: pysimiam_roboloop.py SUPERVISORCLASS")
    else:
        RoboLoop(7788, helpers.load_by_name(sys.argv[1],'supervisors')).run()


#!/usr/bin/env python3

"""Main."""

import sys
from cpu_additions import *

cpu = CPU()

cpu.load(sys.argv[1]) # sys.argv[1]
cpu.run()
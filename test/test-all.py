#!/usr/bin/env python

"""
Unit testing for EB.  Please keep this file tidy.
Copyright 2013 Andrew Kester, released under GNU GPLv3
"""

import unittest

# Append our path so we can include the EB classes
import sys
sys.path.append('../src')

import backup

class testEBFull(unittest.TestCase):
    # Create an instance of all of the EB classes
    ebm = backup.EBMain()
    ebt = backup.EBThreading()
    ebd = backup.EBDatabase()

if __name__ == '__main__':
    unittest.main()
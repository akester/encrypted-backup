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
    
    # Test configuration parsing
    def test_configParsing(self):
        print 'Checking configuration file parsing...'
        # Check file locations
        self.assertEqual(self.ebm.configFileLocation, '../cfg/eb.conf')
        # Check parsing functions
        self.assertEqual(self.ebm.parseConfig(), {'main': {'key': 'value'}})
        

if __name__ == '__main__':
    unittest.main()
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
    
    # Test the imports and declarations above
    def test_imports(self):
        self.assertIsInstance(self.ebm, backup.EBMain)
        self.assertIsInstance(self.ebt, backup.EBThreading)
        self.assertIsInstance(self.ebd, backup.EBDatabase)
    
    # Test configuration parsing
    def test_configParsing(self):
        # Check file locations
        self.assertEqual(self.ebm.configFileLocation, '../cfg/eb.conf')
        # Check parsing functions
        # This variable should equal the test config's keys and values.
        cfgData = {'main': { 'key':'value'
                            }
                   }
        self.assertEqual(self.ebm.parseConfig(), cfgData, 'CFG Data is invalid.')
        

if __name__ == '__main__':
    unittest.main()
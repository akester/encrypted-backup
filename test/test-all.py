#!/usr/bin/env python

"""
Unit testing for EB.  Please keep this file tidy.
Copyright 2013 Andrew Kester, released under GNU GPLv3
"""

import unittest
import os
import shutil

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
        cfgData = {'main': { 'keyid':'8807C3E8'
                            }
                   }
        self.assertEqual(self.ebm.parseConfig(), cfgData, 'CFG Data is invalid.')
        
    # Test file hashing
    def test_fileHashing(self):
        # Hash a file
        self.assertEqual(self.ebm.getFileHash('files/hacking.txt'), '142ed81e48888c141c64e27215d99ce14d52f829',
                         'Test data is not consistent')
        # Hash a small directory
        self.assertEqual(self.ebm.getDirHash('directory/10'), '1337b77ae713094ad3d6b99302cd08a46d9fce5f',
                         'Test data is not consistent')
        # Hash a larger directory
        self.assertEqual(self.ebm.getDirHash('directory'), '0dfcc0df20c63b1a010e8a4d14f3208a6f6df32f',
                         'Test data is not consistent')
        
        
    # Check tarball compression
    def test_tar(self):
        self.ebm.archiveDirectory('directory/10', 'tmp/10.tar')
        # Check that the file exists and we can decompress it (ie, it is a tar file)
        try:
            self.ebm.dearchiveDirectory('tmp/10.tar')
        except:
            self.fail('Could not extract tar archive')
            
        # Ensure that we have the same data
        self.assertEqual(self.ebm.getDirHash('tmp/directory/10'), '1337b77ae713094ad3d6b99302cd08a46d9fce5f',
                         'Extracted data is not consistent')
            
        #Clean the files
        os.remove('tmp/10.tar')
        shutil.rmtree('tmp/directory')
        

if __name__ == '__main__':
    unittest.main()
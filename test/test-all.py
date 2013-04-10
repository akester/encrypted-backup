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
                         'Test data is not consistent-1')
        # Hash a small directory
        self.assertEqual(self.ebm.getDirHash('directory/10'), '0fe397ded78dcb2b7514ca0ae1f84c53d50ad6c8',
                         'Test data is not consistent-2')
        # Hash a larger directory
        self.assertEqual(self.ebm.getDirHash('directory'), '55363c7595457d2ef37d9fccf8d2f5b5bcc3d978',
                         'Test data is not consistent-3')
        
        
    # Check tarball compression
    def test_tar(self):
        self.ebm.archiveDirectory('directory/10', 'tmp/10.tar')
        # Check that the file exists and we can decompress it (ie, it is a tar file)
        try:
            self.ebm.dearchiveDirectory('tmp/10.tar')
        except:
            self.fail('Could not extract tar archive')
            
        # Ensure that we have the same data
        self.assertEqual(self.ebm.getDirHash('tmp/directory/10'), '0fe397ded78dcb2b7514ca0ae1f84c53d50ad6c8',
                         'Extracted data is not consistent')
        self.assertEqual(self.ebm.getFileHash('tmp/10.tar'), 'db35a6f697992283644719667e0b955605d2c383',
                         'Archive is not consitent.')
            
        try:
            #Clean the files
            os.remove('tmp/10.tar')
            shutil.rmtree('tmp/directory')
        except:
            self.fail('Could not remove tmp extraction data.')
            
    # Check gzip compression
    def test_gzip(self):
        self.ebm.compressFile('files/hacking.txt', 'tmp/hacking.txt.gz')
        try:
            self.ebm.decompressFile('tmp/hacking.txt.gz', 'tmp/hacking.txt')
        except:
            self.fail('Could not decompress archive.')
        
        self.assertEqual(self.ebm.getFileHash('tmp/hacking.txt'), '142ed81e48888c141c64e27215d99ce14d52f829',
                         'Extracted data is not consistent')
        
        try:
            #Clean the files
            os.remove('tmp/hacking.txt.gz')
            os.remove('tmp/hacking.txt')
        except:
            self.fail('Could not remove tmp extraction data.')
            
    # Check database functions
    def test_databaseInit(self):
        self.ebd.initBackupDB('tmp/testfile.sqlite')
        self.assertEqual(self.ebm.getFileHash('tmp/testfile.sqlite'), '0c439b1ea702b2c527e92db55d08b9679f4355cd',
                         'Database is not consistent')
        
        try:
            #Clean the files
            os.remove('tmp/testfile.sqlite')
        except:
            self.fail('Could not remove tmp database data.')
        
# DO NOT EDIT - This will execute all of the tests above!
if __name__ == '__main__':
    unittest.main()
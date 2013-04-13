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
    # Test the imports and declarations
    def test_imports(self):
        ebm = backup.EBMain()
        ebt = backup.EBThreading()
        ebd = backup.EBDatabase('tmp/test-database.sql')

        try:
            self.assertIsInstance(ebm, backup.EBMain)
            self.assertIsInstance(ebt, backup.EBThreading)
            self.assertIsInstance(ebd, backup.EBDatabase)
        except AttributeError:
            pass
        
        try:
            #Clean the files
            os.remove('tmp/test-database.sql')
        except:
            self.fail('Could not remove tmp database.')
    
    # Test configuration parsing
    def test_configParsing(self):
        ebm = backup.EBMain()
        # Check file locations
        self.assertEqual(ebm.configFileLocation, '../cfg/eb.conf')
        # Check parsing functions
        # This variable should equal the test config's keys and values.
        cfgData = {'main': { 'keyid':'8807C3E8'
                            }
                   }
        self.assertEqual(ebm.parseConfig(), cfgData, 'CFG Data is invalid.')
        
    # Test file hashing
    #def test_fileHashing(self):
    #    ebm = backup.EBMain()
    #    # Hash a file
    #    self.assertEqual(ebm.getFileHash('files/hacking.txt'),
    #                     '142ed81e48888c141c64e27215d99ce14d52f829',
    #                     'Test data is not consistent-1')
    #    # Hash a small directory
    #    self.assertEqual(ebm.getDirHash('directory/10'),
    #                     '0fe397ded78dcb2b7514ca0ae1f84c53d50ad6c8',
    #                     'Test data is not consistent-2')
    #    # Hash a larger directory
    #    self.assertEqual(ebm.getDirHash('directory'),
    #                     '55363c7595457d2ef37d9fccf8d2f5b5bcc3d978',
    #                     'Test data is not consistent-3')
        
        
    # Check tarball compression
    def test_tar(self):
        ebm = backup.EBMain()
        ebm.archiveDirectory('directory/10', 'tmp/10.tar')
        # Check that the file exists and we can decompress it (ie, it is a tar file)
        try:
            ebm.dearchiveDirectory('tmp/10.tar')
        except:
            self.fail('Could not extract tar archive')
            
        # Ensure that we have the same data
        #self.assertEqual(ebm.getDirHash('tmp/directory/10'),
        #                 '0fe397ded78dcb2b7514ca0ae1f84c53d50ad6c8',
        #                 'Extracted data is not consistent')
        #self.assertEqual(ebm.getFileHash('tmp/10.tar'),
        #                 'db35a6f697992283644719667e0b955605d2c383',
        #                 'Archive is not consitent.')
            
        try:
            #Clean the files
            os.remove('tmp/10.tar')
            shutil.rmtree('tmp/directory')
        except:
            self.fail('Could not remove tmp extraction data.')
            
    # Check gzip compression
    def test_gzip(self):
        ebm = backup.EBMain()
        ebm.compressFile('files/hacking.txt', 'tmp/hacking.txt.gz')
        try:
            ebm.decompressFile('tmp/hacking.txt.gz', 'tmp/hacking.txt')
        except:
            self.fail('Could not decompress archive.')
        
        #self.assertEqual(ebm.getFileHash('tmp/hacking.txt'),
        #                 '142ed81e48888c141c64e27215d99ce14d52f829',
        #                 'Extracted data is not consistent')
        
        try:
            #Clean the files
            os.remove('tmp/hacking.txt.gz')
            os.remove('tmp/hacking.txt')
        except:
            self.fail('Could not remove tmp extraction data.')
            
    # Check database functions
    def test_database(self):
        ebd = backup.EBDatabase('tmp/test-db-init.sql')
        ebm = backup.EBMain()
        ebd.initBackupDB()
        #self.assertEqual(ebm.getFileHash('tmp/test-db-init.sql'),
        #                 '0c439b1ea702b2c527e92db55d08b9679f4355cd',
        #                 'Database creation is not consistent')
        
        # Test some data
        ebd.storeChunkInformation(1, '1000-1.tar.gz')
        
        #self.assertEqual(ebm.getFileHash('tmp/test-db-init.sql'), 
        #                 'c81cf92e0bc0d9fb159761a7cd220ac9fdfafeb1',
        #                 'Database storage is not consistent')
        
        # Test a read
        # This var should be the chunks we will get from above
        chunks = {1:'1000-1.tar.gz'}
        self.assertEqual(ebd.getChunks(), chunks,
                         'Data fetch was not consitent')
        
        del ebd
        
        try:
            #Clean the files
            os.remove('tmp/test-db-init.sql')
        except:
            self.fail('Could not remove tmp database data.')
            
    # Test file chunking
    def test_chunkingHelpers(self):
        ebm = backup.EBMain()
        size = ebm.getFileSize('files/archive.tar')
        chunks = ebm.calculateChunks(size, 1000)
        
        self.assertEqual(size, 563200)
        self.assertEqual(chunks, 564)
        self.assertEqual(ebm.getFileData('files/oneline.txt'),
                         'The quick fox jumed over the lazy brown dog.')
        self.assertEqual(ebm.getFileName('files/archive.tar'), 'archive.tar')
        
    def test_chunkingMain(self):
        ebm = backup.EBMain()
        self.assertEqual(ebm.chunkFile('files/archive.tar', 'tmp/archive', 1000),
                         564)
        
        if not os.path.isdir('tmp/archive'):
            self.fail('Output Directory Failed')
        
        # Clean the files
        try:
            shutil.rmtree('tmp/archive')
        except:
            self.fail('Could not remove chunked file')
            
    # Test the Split chunking
    def test_chunkingSplit(self):
        ebm = backup.EBMain()
        self.assertEqual(ebm.chunkFileSplit('files/archive.tar', 
                                           'tmp/archive/','archive', 1000), 564)
        
        if not os.path.isdir('tmp/archive'):
            self.fail('Output Directory Failed')
        
        # Clean the files
        try:
            shutil.rmtree('tmp/archive')
        except:
            self.fail('Could not remove chunked file')
                
# DO NOT EDIT - This will execute all of the tests above!
if __name__ == '__main__':    
    unittest.main()
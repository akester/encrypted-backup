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
        cfgData = {'main': { 'keyid':'282C7943'
                            },
                   '10': { 'days':'1',
                          'local':'../test/directory/10',
                          'remote':'/tmp',
                          'mounted':'true'
                          },
                   '10-2': { 'days':'1',
                            'local':'../test/directory/10',
                            'remote':'/tmp',
                            'mounted':'false',
                            'pre':'uname',
                            'post':'uname'
                            }
                   }
        self.assertEqual(ebm.parseConfig(), cfgData, 'CFG Data is invalid.')        
        
    # Check tarball compression
    def test_tar(self):
        ebm = backup.EBMain()
        ebm.archiveDirectory('directory/10', 'tmp/10.tar')
        # Check that the file exists and we can decompress it (ie, it is a tar file)
        try:
            ebm.dearchiveDirectory('tmp/10.tar', 'tmp/.')
        except:
            self.fail('Could not extract tar archive')
            
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
        
        try:
            #Clean the files
            os.remove('tmp/hacking.txt.gz')
            os.remove('tmp/hacking.txt')
        except:
            self.fail('Could not remove tmp extraction data.')
            
    # Check database functions
    def test_databaseChunks(self):
        ebd = backup.EBDatabase('tmp/test-db-init.sql')
        ebm = backup.EBMain()
        ebd.initBackupDB()
        
        # Test some data
        ebd.storeChunkInformation(1, '1000-1.tar.gz', 1)
        
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
            
    def test_databaseMeta(self):
        ebd = backup.EBDatabase('tmp/test-db-meta.sql')
        ebm = backup.EBMain()
        ebd.initBackupDB()
        
        ebd.storeMeta('testkey', 'testvalue')
        
        meta = {'testkey':'testvalue'}
        self.assertEqual(ebd.getMeta(), meta)
        
        del ebd
        
        try:
            #Clean the files
            os.remove('tmp/test-db-meta.sql')
        except:
            self.fail('Could not remove tmp database data.')
            
    def test_databaseRuns(self):
        ebd = backup.EBDatabase('tmp/test-db-runs.sql')
        ebm = backup.EBMain()
        ebd.initBackupDB()
        
        ebd.c.execute('INSERT INTO runs VALUES (0, 1)')
        ebd.db.commit()
        
        # This should equal the data inserted
        row = {0:1}
        self.assertEqual(row, ebd.getRunStatus(1))        
            
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
        self.assertEqual(ebm.chunkFile('files/archive.tar', 'tmp/archive1', 1000),
                         564)
        
        if not os.path.isdir('tmp/archive1'):
            self.fail('Output Directory Failed')
        
        
        # Clean the files
        try:
            shutil.rmtree('tmp/archive1')
        except:
            self.fail('Could not remove chunked file')
            
    # Test the Split chunking
    def test_chunkingSplit(self):
        ebm = backup.EBMain()
        self.assertEqual(ebm.chunkFileSplit('files/archive.tar', 
                                           'tmp/archive2/','archive', 1000), 564)
        
        if not os.path.isdir('tmp/archive2'):
            self.fail('Output Directory Failed')
            
        ebm.assembleChunksCat('tmp/archive2/*', 'tmp/testout2.tar')
        
        # Clean the files
        try:
            shutil.rmtree('tmp/archive2')
            #os.remove('tmp/testout2.tar')
        except:
            self.fail('Could not remove chunked file')
            
    def test_date(self):
        ebm = backup.EBMain()
        self.assertEqual(ebm.getDate(123456), 'Fri Jan  2 04:17:36 1970')
                
# DO NOT EDIT - This will execute all of the tests above!
if __name__ == '__main__':    
    unittest.main()
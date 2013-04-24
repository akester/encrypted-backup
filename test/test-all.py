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
        ebe = backup.EBEncryption('tmp')

        try:
            self.assertIsInstance(ebm, backup.EBMain)
            self.assertIsInstance(ebe, backup.EBEncryption)
        except AttributeError:
            pass

    # Test configuration parsing
    def test_configParsing(self):
        ebm = backup.EBMain()
        # Check file locations
        self.assertEqual(ebm.configFileLocation, '../cfg/eb.conf')
        # Check parsing functions
        # This variable should equal the test config's keys and values.
        cfgData = {'main': { 'keyid':'704A6507',
                            'passp':'passphrase'
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
            
        try:
            #Clean the files
            os.remove('tmp/10.tar')
        except:
            self.fail('Could not remove tmp extraction data.')
           
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
            os.remove('tmp/testout2.tar')
        except:
            self.fail('Could not remove chunked file')
            
    def test_fileJoinsCat(self):
        ebm = backup.EBMain()
        self.assertEqual(ebm.chunkFileSplit('files/oneline.txt', 
                                            'tmp/test-joins', 'join', 10), 
                         5)
        
        ebm.assembleChunksCat('tmp/test-joins/join*', 'tmp/oneline.txt')
        self.assertEqual(ebm.getFileData('tmp/oneline.txt'), 
                         'The quick fox jumed over the lazy brown dog.')
        
        # Clean the files
        try:
            shutil.rmtree('tmp/test-joins')
            os.remove('tmp/oneline.txt')
        except:
            self.fail('Could not remove file')
    
    # Encrypt/Decrypt
    def test_encryption(self):
        ebe = backup.EBEncryption('/home/andrew/.gnupg')
        ebm = backup.EBMain()
        
        exit = ebe.encryptFile('files/oneline.txt', 'tmp/outfile-c.txt', '704A6507', 
                               'passphrase')
        self.assertEqual(exit, 'encryption ok')
        
        exit = ebe.decryptFile('tmp/outfile-c.txt', 'tmp/oneline-c.txt',
                               'passphrase')
        self.assertEqual(exit, 'decryption ok')
        
        # Verify Contents
        self.assertEqual(ebm.getFileData('tmp/oneline-c.txt'),
                         'The quick fox jumed over the lazy brown dog.')
        
        try:
            os.remove('tmp/oneline-c.txt')
            os.remove('tmp/outfile-c.txt')
        except:
            self.fail('Could not remove file')
        
        
                
# DO NOT EDIT - This will execute all of the tests above!
if __name__ == '__main__':    
    unittest.main()
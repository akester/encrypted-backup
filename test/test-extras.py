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

class testEBExtras(unittest.TestCase):
        # Test chunking of a large file
    def test_largeFileChunkingSplit(self):
        ebm = backup.EBMain()
        self.assertEqual(ebm.chunkFileSplit('files/large-text.txt', 
                                            'tmp/large-text/', 'txt1', 1000000),
                         394)
        
        if not os.path.isdir('tmp/large-text'):
            self.fail('Output Directory Failed')
            
        ebm.assembleChunksCat('tmp/large-text/txt1*', 'tmp/testout-large.tar')
        
        # Clean the files
        try:
            shutil.rmtree('tmp/large-text')
        except:
            self.fail('Could not remove chunked file')
            
#    def test_largeFileChunking(self):
#        ebm = backup.EBMain()
#        self.assertEqual(ebm.chunkFile('files/large-text.txt', 'tmp/large-text', 
#                                       1000000), 394)
#         
#        if not os.path.isdir('tmp/large-text'):
#            self.fail('Output Directory Failed')
#        
#                # Clean the files
#        try:
#            shutil.rmtree('tmp/large-text')
#        except:
#            self.fail('Could not remove chunked file')
                
# DO NOT EDIT - This will execute all of the tests above!
if __name__ == '__main__':    
    unittest.main()
#!/usr/bin/env python

"""
A Program to create chunked snapshot backups and encrpyt the resulting files.  Will also
Manage the files in a local or seperate file system, allowing for the encrpyted files
to be stored in an offiste filesystem (either a custom setup or a service like Amazon
Glacier)

This program is copyright 2013 Andrew Kester, released under the GNU General Public License
version 3 or, at your option, any later version.
"""

## Imports
#from multiprocessing import Pool
import argparse
#import sqlite3
import ConfigParser
import datetime
import hashlib
import os
import sys
import errno

"""
Main EB Functions
"""
class EBMain:
    """
    System-specific Variables
    """
    # The location of the configuration files (default: /etc/eb/eb.conf
    configFileLocation = '../cfg/eb.conf'
    
    """
    A wrapper for configuration file parsing
    """
    def parseConfig(self):
        # Read the configuration file
        try:
            config = ConfigParser.SafeConfigParser()
            config.read(self.configFileLocation)
        except ConfigParser.Error as e:
            sys.stdout.write('Error parsing configuration.  Returned: {0}\n'.format(e))
            sys.stdout.flush()
            exit(-errno.EIO)
        
        # Build the file into a dict that we can use
        out = {}
        for section in config.sections():
            out[section] = {}
            for option in config.options(section):
                out[section][option] = config.get(section, option)
                
        return out
        
    """
    Extracts a tar archive
    """        
    def dearchiveDirectory(self, tar):
        tar = tarfile.open(tar)
        tar.extractall('tmp/.')
        tar.close()
        
    """
    Gets the hash of a file
    """
    def getFileHash(self, path):
        sha1 = hashlib.sha1()
        f = open(path)
        try:
            sha1.update(f.read())
        finally:
            f.close()
        return sha1.hexdigest()
    
    """
    Gets the hash of a directory
    """
    def getDirHash(self, path):
        sha1 = hashlib.sha1()
        tree = os.walk(path)
        for root, dirs, files in tree:
            for f in files:
                sha1.update(self.getFileHash(root + '/' + f))
                
        return sha1.hexdigest()
    
"""
Threading functions and operations
"""
class EBThreading:
    pass

"""
Database operations
"""
class EBDatabase:
    pass


if __name__ == '__main__':
    ## Argument Parsing
    parser = argparse.ArgumentParser(description="A program to create snapshot backups.")
    
    args = parser.parse_args()
    
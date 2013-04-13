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
import ConfigParser
import datetime
import gzip
import hashlib
import os
import sqlite3
from subprocess import call
import sys
import tarfile
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
    Generates the hash for this snapshot
    """
    def generateSnapshotHash(self):
        datestr = datetime.datetime.today().strftime("%I:%M%p on %B %d, %Y")
        return hashlib.sha1(datestr).hexdigest()
    
    """
    Archive a directory
    """
    def archiveDirectory(self, directory, outfile):
        tar = tarfile.open(outfile, "w")
        tar.add(directory)
        tar.close()
        
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
    Compress a file
    """
    def compressFile(self, path, outpath):
        f = gzip.open(outpath, 'wb')
        f_in = open(path, 'rb')
        f.writelines(f_in)
        f.close()
    
    """
    Decompress a file
    """
    def decompressFile(self, path, outpath):
        f = gzip.open(path)
        f_out = open(outpath, 'w+')
        f_out.writelines(f.read())
        
    """
    Get the size of a file
    """
    def getFileSize(self, path):
        return os.path.getsize(path)
    
    """
    Determine the number of chunks we will need
    """
    def calculateChunks(self, size, csize):
        chunks = size / csize
        if (size % csize):
            chunks += 1
        
        return chunks
    
    """
    Gets a file's data
    """
    def getFileData(self, path):
        f = open(path, 'rb')
        data = f.read()
        f.close()
        
        return data
    
    """
    Gets a file name
    """
    def getFileName(self, path):
        return os.path.basename(path)
    
    def chunkFile(self, inpath, outpath, csize):
        size = self.getFileSize(inpath)
        chunks = self.calculateChunks(size, csize)
        data = self.getFileData(inpath)
        filename = self.getFileName(inpath)
        
        # Create an output directory
        if not os.path.isdir(outpath):
            os.mkdir(outpath)
        
        # Write the output files
        i = 1
        while i <= chunks:
            outName = outpath + '/' + filename + '.' + str(i)
            
            f = open(outName, 'wb')
            f.write(data[i:i + csize])
            f.close()
            
            i += 1
            
        return chunks
    
    """
    Another method of chunking files, this one uses the Linux Split commmand
    It's less cross platform friendly, but splitting large files with the above
    commands might use too much ram (since we are reading the entire file into
    RAM, then chunking the file.
    """
    def chunkFileSplit(self, inpath, outpath, prefix, csize):
        #TODO: Determine number of digits and pass that to split
        size = self.getFileSize(inpath)
        chunks = self.calculateChunks(size, csize)
        
        digits = len(str(chunks)) 
        # Create an output directory
        if not os.path.isdir(outpath):
            os.mkdir(outpath)
            
        outprefix = outpath + '/' + prefix
            
        call(["split", "-b " + str(csize), "-d", "-a " + str(digits),
              inpath, outprefix])
        return chunks
    
"""
Threading functions and operations
"""
class EBThreading:
    pass

"""
Database operations
"""
class EBDatabase:
    # Location of the database file we are using.
    path = None
    db = None
    c = None
    
    """
    Connect to a database
    """
    def __init__(self, path):
        self.path = path
        self.db = sqlite3.connect(self.path)
        self.c = self.db.cursor()
    
    """
    Close the db connection
    """
    def __del__(self):
        self.c.close()    
        
    """
    Create a database to be stored with the backups
    """
    def initBackupDB(self):        
        self.c.execute("CREATE TABLE IF NOT EXISTS chunks (id int, name text)")
        self.c.execute("CREATE TABLE IF NOT EXISTS meta (key test, value test)")
        self.db.commit()
        
    """
    Stores a chunk
    """
    def storeChunkInformation(self, cid, name):        
        self.c.execute("INSERT INTO chunks VALUES ({0}, '{1}')".format(cid, name))
        self.db.commit()
        
    """
    Gets all of the chunks and thier files
    """
    def getChunks(self):
        out = {}
        for row in self.c.execute("SELECT * FROM chunks WHERE 1"):
            out[row[0]] = row[1]
        return out
    
    """
    Stores metadata
    """
    def storeMeta(self, key, value):
        self.c.execute("INSERT INTO meta VALUES('{0}', '{1}')".format(key, value))
        self.db.commit()
        
    """
    Gets metadata
    """
    def getMeta(self, key = '%'):
        out = {}
        for row in self.c.execute("SELECT * FROM meta WHERE key LIKE '{0}'"
                                  .format(key)):
            out[row[0]] = row[1]
        return out
            
        

if __name__ == '__main__':
    ## Argument Parsing
    parser = argparse.ArgumentParser(description="A program to create snapshot backups.")
    
    args = parser.parse_args()
    
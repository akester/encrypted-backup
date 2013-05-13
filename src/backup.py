#!/usr/bin/env python

"""
A Program to create chunked snapshot backups and encrpyt the resulting files.

This program is copyright 2013 Andrew Kester, released under the GNU General
Public License version 3 or, at your option, any later version.
"""

## Imports
import argparse
import ConfigParser
import gnupg
import os
import shutil
import subprocess
import sys
import tarfile
import time
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
            sys.stdout.write('Error parsing configuration.  Returned: {0}\n'
                             .format(e))
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
    Archive a directory
    """
    def archiveDirectory(self, directory, outfile):
        tar = tarfile.open(outfile, "w")
        try:
            tar.add(directory)
        except WindowsError:
            pass
        tar.close()

    """
    Get the size of a file
    """
    def getFileSize(self, path):
        return os.path.getsize(path)
    
    """
    Determine the number of chunks we will need
    """
    def calculateChunks(self, size, csize):
        chunks = size / int(csize)
        if (size % int(csize)):
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
    
    """
    Another method of chunking files, this one uses the Linux Split commmand
    It's less cross platform friendly, but splitting large files with the above
    commands might use too much ram (since we are reading the entire file into
    RAM, then chunking the file.
    """
    def chunkFileSplit(self, inpath, outpath, prefix, csize):
        size = self.getFileSize(inpath)
        chunks = self.calculateChunks(size, csize)
        
        digits = len(str(chunks)) 
        # Create an output directory
        if not os.path.isdir(outpath):
            os.mkdir(outpath)
            
        outprefix = str(outpath) + '/' + str(prefix)
            
        subprocess.call(["split", "--bytes=" + str(csize), "-d", "-a " 
                         + str(digits), inpath, outprefix])
        return chunks
    
    """
    Reassembles a chunked file using cat
    """
    def assembleChunksCat(self, inpath, outpath):
        f = open(outpath, 'w+')
        output = subprocess.Popen('cat ' + inpath, shell=True, stdout=f)
        output.communicate()
        f.close()
        return output
    
    """
    Reassembles a chunked file
    
    This function does not return data in order (a limitation of os.walk)
    """
 
"""
Encryption Functions
"""
class EBEncryption:
    def __init__(self, keyring):
        self.gpg = gnupg.GPG(gnupghome=keyring)
        
    def encryptFile(self, infile, outfile, key, passp):
        f = open(infile)
        crypt = self.gpg.encrypt_file(f, key, output=outfile, passphrase=passp,
                                      always_trust=True)
        f.close()
        
        return crypt.status
        
    
    def decryptFile(self, infile, outfile, passp):
        f = open(infile)
        crypt = self.gpg.decrypt_file(f, output=outfile, passphrase=passp)
        f.close()
        
        return crypt.status

if __name__ == '__main__':
    
    ## Argument Parsing
    parser = argparse.ArgumentParser(description="A program to create snapshot" 
                                     + " backups.")
    parser.add_argument('--path', required=True, dest="path", 
                        help="Source path to back up")
    parser.add_argument('--outpath', required=True, dest="outpath",
                         help="Output path of files to be copied.")
    parser.add_argument('--tmppath', required=True, dest="tmppath", 
                        help="Temporary Output path of files to be copied.")
    parser.add_argument('--csize', required=False, dest="csize", 
                        default="100000", 
                        help="The size, in bytes, of each file chunk")
    parser.add_argument('--restore', required=False, dest="rest", 
                        action="store_true", default=False, 
                        help="Restore the files from --path rather than encrypt"
                        + " them.")

    parser.add_argument('--noe', required=False, dest="noe",
                        action="store_true", default=False,
                        help="Do not encrypt resulting files")
    args = parser.parse_args()

    ebm = EBMain()

    if not args.noe:
        ebe = EBEncryption(os.path.expanduser('~/.gnupg'))
    
        cfg = ebm.parseConfig()
        
        try:
            cfg['main']['keyid'] = cfg['main']['keyid']
            cfg['main']['passp'] = cfg['main']['passp']
        except KeyError as e:
            sys.stderr.write('E: Missing configuration value {0}\n'.format(e))
            exit(errno.EINVAL)
    

    # Make sure the path exists
    if not os.path.isdir(args.path) and not os.path.isfile(args.path):
        sys.stderr.write('E: Path ({0}) does not exist.\n'
                         .format(args.path))
        exit(errno.ENOENT)
            
    # Make a tmp file (it could be too large for /tmp to handle and we want
    # the files in case the system crashes/reboots during our operations)
    if not os.path.isdir(args.tmppath):
        try:
            os.mkdir(args.tmppath)
        except OSError as e:
            sys.stdout.write('E: Could not create output directory: {0}\n'
                             .format(e))
            exit(errno.EIO)
                        
    # Archive the files
    sys.stdout.write('Taring files...\n')
    ebm.archiveDirectory(args.path, args.tmppath + '/eb-tmp.tar')
    ebm.chunkFileSplit(args.tmppath+'/eb-tmp.tar', args.tmppath, 
                       str(time.time()) + '_', args.csize)
    
    # Remove the original tmp tar file
    os.remove(args.tmppath + '/eb-tmp.tar')
    
    if not args.noe:
        # Encrypt the files using the key provided
        for root, dirs, files in os.walk(args.tmppath):
            numFiles = len(files)
            x=0
            for f in files:
                x += 1
                status = ebe.encryptFile(root + '/' + f, args.outpath + '/' 
                                         + f + '.pgp', cfg['main']['keyid'], 
											cfg['main']['passp'])
                if status != 'encryption ok':
                    sys.stderr.write('E: Encryption Error.')
                    exit(1)
                sys.stdout.write('Encrypted file {0} of {1}\n'
                                 .format(x, numFiles))

    shutil.rmtree(args.tmppath)
            
    exit(0)

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
from multiprocessing import Pool
import argparse
import sqlite3
import ConfigParser

"""
Main EB Functions
"""
class EBMain:
    pass

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
    
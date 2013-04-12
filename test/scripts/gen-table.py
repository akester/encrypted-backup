# A script for generating random strings of characters. (sp)
#
# Obviously the author is not responsible for how this script is used.  It
# is designed for private reasearch.  Usage of this file can be illegal in
# certain contexts.  USE AT YOUR OWN RISK.
#
# The nice keyboard interrupt handling is originally by John Reese.
# That code (Lines 95-96, 137-146) is Copyright (c) 2011 Jonhn Reese
# and released under the MIT License.
#
# The remainder of this program is Copyright (c) 2012 Andrew Kester and
# released under GNU-GPLv3
#
# This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Imports
import argparse
from multiprocessing import Pool
import os
import signal
import time

parser = argparse.ArgumentParser(description='Generates random tables of charecters to brute passwords with.')

parser.add_argument('--min', '-i', help='The minimum number of chars to generate.', required=False, default=1, dest='min', type=int)
parser.add_argument('--max', '-x', help='The maximum number of chars to generate.', required=False, default=25, dest='max', type=int)
parser.add_argument('--out', '-o', help='The outfile to write', required=False, dest='outfile')
parser.add_argument('--print', '-p', help='Print the data rather than write it to a file', required=False, dest='p', default=False, action='store_true')

parser.add_argument('--threads', '-t', help='The number of threads to spawn', required=False, dest='threads', default=1)

args = parser.parse_args()

# This is all of the valid charecters that are used to generate strings.
valid = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ`1234567890-=~!@#$%^&*()_+,./;\'[]\<>?:\"{}|'

# Stores completed runs.
c = []

# Used for error reporting
e = 254

# This is the function that recurses to construct the string
def addStr(chars, test, outfile):
    global x
    global valid

    chars -= 1
    test += '.'

    for l in valid:
        test = test[0:-1]
        test += l
        
        if (chars <= 0):
            # Write the data to the file
            if (args.p==True):
                print test
            else:
                out.write('{}\n'.format(test))
        else:
            # Recurse
            addStr(chars, test, out)

# This is what initiates the function above, outputs some data to the user as well.
def runString(chars, test, outfile):
    if (args.p==False):
        print '++++ Starting background generation of {} combinations.'.format(chars)

    # Do the work
    addStr(chars, test, outfile)

    if (args.p == False):
        print '---- Worker for {} combinations complete.'.format(chars)
    #Return for callback
    return chars

# This is the callback function that lets our monitor script know we've completed a round.
def complete(x):
    c.append(x)
    return True

# Used to kill workers
def int_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)

# Try to open the output file.
# TODO: Won't create a file.
if (args.p == False):
    try:
        #with open(args.outfile) as out: pass
        out = open(args.outfile, 'w+')
    except IOError as e:
        print 'E: Could not open output file \'{}\' ({}).'.format(args.outfile, e.strerror)
        e = 1
        exit(e)
else:
    out = ''

pool = Pool(int(args.threads), int_worker)

# Queue all our work, the pool will take care of assignments/threading.
for x in range(int(args.min), int(args.max) + 1):
    pool.apply_async(runString, [x, '', out], callback=complete)

try:
    # Periodically check the status of the workers
    run = True
    t = 0
    # We check like this rather than pool.join() to avoid hanging on pool.join
    # If a user interrupts, pool.join will wait before the exception is thrown.
    # Checking this way is a bit more involved, however lets a user throw an 
    # interrupt at any time during execution and stop the workers.
    while run == True:
        t += 1
        run = False
        for x in range(int(args.min), int(args.max) + 1):
            # If we still have data out, sleep
            if x not in c:
                run = True
        time.sleep(1)
    if (args.p==False):
        print 'All workers completed in {} seconds'.format(t)

# User threw an interrupt.
except KeyboardInterrupt:
    print 'Caught keyboard interrupt, killing the pool'
    pool.terminate()
    pool.join()
    e = 2
# All workers exitied, we can exit normally.
else:
    pool.close()
    pool.join()
    e = 0

if (args.p==False):
    # Close the file, if we had lots of data this can take a few seconds.
    print 'Closing file...'
    out.close()

exit(e)

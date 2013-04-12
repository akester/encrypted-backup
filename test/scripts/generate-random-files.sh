# A script to generate files with random file sizes.
# Idea taken from rajaseelan.com, adapted by Andrew Kester
# Copyright 2013 Andrew Kester, Released under GNU-GPLv3

files=$1;
outdir=$2

x=1;
while [[ $x -le $files ]];
 do echo Creating file no $x;
  size=`shuf -i 1-100 -n 1`
  dd bs=1024 count=$size skip=$RANDOM if=/dev/urandom of=$outdir/random-file.$x 1> /dev/null;
  let "x += 1";
 done

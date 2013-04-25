#!/bin/bash

#########################################
# EB Example cron script.		#
# Copyright 2013 Andrew Kester		#
# Released under GNU-GPL		#
#########################################

# Set this var to set the input paths you want to backup
backups=('/home/andrew/Projects/servus' '/home/andrew/Documents')

# Set this var to the output location to store backups (subdirectories will be
# created automatically)
outpath='../test/tmp/'

# Set this to the tmp directory you would like to use
tmppath='/tmp/eb'

# For each backup iterate through the backup and run eb on it
for b in "${backups[@]}"
do
	date=`date | sed -e 's/ /-/g'`
	ob=$outpath'/'$b'/'$date
	mkdir -p "$ob"
	echo "Backing up $b into $ob"
	if [ $? -ne 0 ]
	then
		echo "E: Could not create output dir" 1>&2
		exit 1
	fi
	python backup.py --path "$b" --outpath "$ob" --tmppath "$tmppath" --csize 1000000000
done

# Obviously replace this command with whatever it is you use to sync your data
s3cmd push --recusrive indir outbucket

# Clean up the outdirs
rm -r $outpath'/*'

#!/bin/bash

# Get the latest repo
cd ..
git pull origin master

echo 'Testing Mains...'
python test-all.py
echo 'Testing Extras...'
python test-extras.py

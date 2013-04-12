#!/bin/bash

echo "WARNING!"
echo "This script will generate a large file in the project directory."
echo "Starting in 5 seconds..."

sleep 5

python gen-table.py --threads 4 --out ../files/large-text.txt --min 1 --max 6

#!/bin/bash

REL_PATH=`dirname "$0"`
CANONICAL_PATH=`readlink -f $REL_PATH`

#For Server's invention that server cmdline must start
#on the code's folder, cd(change directory) needed.
cd $CANONICAL_PATH
cd ../
python3 ./pyttsbot.py
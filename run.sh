#!/bin/bash

DIRECTORY=`dirname $0`

if [ -d "$DIRECTORY/venv" ]; then
    source venv/bin/activate
else
    echo "Python virtual environment does not exist!"
    echo "Please execute build.sh before running."
    exit 1
fi;

PYTHONPATH=$DIRECTORY python3 $DIRECTORY/src/main.py "$@"

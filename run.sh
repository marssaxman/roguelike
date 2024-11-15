#!/bin/bash

DIRECTORY=`dirname $0`

if [ -d "$DIRECTORY/venv" ]; then
    source venv/bin/activate
fi;

PYTHONPATH=$DIRECTORY python3 $DIRECTORY/src/main.py "$@"

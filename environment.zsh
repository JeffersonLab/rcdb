#!/bin/bash

# Get script directory
SCRIPT_PATH=$0:a:h;

#set our environment
export RCDB_HOME=$SCRIPT_PATH 
export LD_LIBRARY_PATH="$RCDB_HOME/lib":$LD_LIBRARY_PATH
export PYTHONPATH="$RCDB_HOME/python":$PYTHONPATH
export PATH="$RCDB_HOME":$PATH


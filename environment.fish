#!/usr/bin/fish

#me Get script directory
set SCRIPT_PATH (dirname (status -f))

#set our environment
set -x RCDB_HOME $SCRIPT_PATH 
set LD_LIBRARY_PATH "$RCDB_HOME/lib" $LD_LIBRARY_PATH
set PYTHONPATH "$RCDB_HOME/python" $PYTHONPATH
set PATH "$RCDB_HOME" $PATH


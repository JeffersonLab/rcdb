#!/usr/bin/fish

#me Get script directory
set SCRIPT_PATH (dirname (status -f))

set FULL_SCRIPT_PATH (readlink -f $SCRIPT_PATH)

#set our environment
set -x RCDB_HOME $FULL_SCRIPT_PATH
echo $RCDB_HOME
set LD_LIBRARY_PATH "$RCDB_HOME/cpp/lib" $LD_LIBRARY_PATH
set PYTHONPATH "$RCDB_HOME/python" $PYTHONPATH
set PATH "$RCDB_HOME" "$RCDB_HOME/cpp/bin" "$RCDB_HOME/bin" $PATH



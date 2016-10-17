#!/bin/csh

set called=($_)
if ("$called" != "") then    
    set name=$called[2]
    set full_path=`readlink -f $name`
    set full_path=`dirname $full_path`
    
else
    echo "This script is to source environment variables for run configuration database"
    echo "So please source it"
    exit(1)
endif

#set our environment
if ( ! $?RCDB_HOME ) then
    setenv RCDB_HOME $full_path
endif
if (! $?LD_LIBRARY_PATH) then
    setenv LD_LIBRARY_PATH $RCDB_HOME/cpp/lib
else
    setenv LD_LIBRARY_PATH "$RCDB_HOME/cpp/lib":$LD_LIBRARY_PATH
endif

if ( ! $?PYTHONPATH ) then
    setenv PYTHONPATH "$RCDB_HOME/python"
else
    setenv PYTHONPATH "$RCDB_HOME/python":$PYTHONPATH
endif
setenv PATH "$RCDB_HOME":"$RCDB_HOME/bin":"$RCDB_HOME/cpp/bin":$PATH

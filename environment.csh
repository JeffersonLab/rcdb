#!/bin/csh
#set our environment
if ( ! $?TDB_HOME ) then
    setenv TDB_HOME `pwd`
endif
if (! $?LD_LIBRARY_PATH) then
    setenv LD_LIBRARY_PATH $TDB_HOME/lib
else
    setenv LD_LIBRARY_PATH "$TDB_HOME/lib":$LD_LIBRARY_PATH
endif
if ( ! $?PYTHONPATH ) then
    setenv PYTHONPATH "$TDB_HOME/python"
else
    setenv PYTHONPATH "$TDB_HOME/python":$PYTHONPATH
endif
setenv PATH "$TDB_HOME/bin":$PATH

#!/bin/csh

set called=($_)
if ("$called" != "") then    
    set name=$called[2]
    echo echo $name >! /tmp/rcdb_csh.tmp
    set name=`source /tmp/rcdb_csh.tmp`
    rm /tmp/rcdb_csh.tmp
    if ("$name" != "") then
	set full_path=`readlink -f $name`
	set full_path=`dirname $full_path`
    endif
else
    echo "environment.csh: This script is to source environment variables for run configuration database"
    echo "So please source it"
    exit(1)
endif

#set our environment
if ( ! $?RCDB_HOME ) then
    if ($?full_path) then 
	setenv RCDB_HOME $full_path
    else
	echo environment.csh: Could not find RCDB_HOME or path to this script
	exit(2)
    endif
endif
if (! $?LD_LIBRARY_PATH) then
    setenv LD_LIBRARY_PATH $RCDB_HOME/cpp/lib
else
    setenv LD_LIBRARY_PATH "$RCDB_HOME/cpp/lib":$LD_LIBRARY_PATH
endif

if (! $?CPLUS_INCLUDE_PATH) then
    setenv CPLUS_INCLUDE_PATH $RCDB_HOME/cpp/include
else
    setenv CPLUS_INCLUDE_PATH "$RCDB_HOME/cpp/include":$CPLUS_INCLUDE_PATH
endif

if ( ! $?PYTHONPATH ) then
    setenv PYTHONPATH "$RCDB_HOME/python"
else
    setenv PYTHONPATH "$RCDB_HOME/python":$PYTHONPATH
endif
setenv PATH "$RCDB_HOME":"$RCDB_HOME/bin":"$RCDB_HOME/cpp/bin":$PATH

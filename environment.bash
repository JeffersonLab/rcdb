#!/bin/bash


#Next lines just finds the path of the file
#Works for all versions,including
#when called via multple depth soft link,
#when script called by command "source" aka . (dot) operator.
#when arg $0 is modified from caller.
#"./script" "/full/path/to/script" "/some/path/../../another/path/script" "./some/folder/script"
#SCRIPT_PATH is given in full path, no matter how it is called.
#Just make sure you locate this at start of the script.
SCRIPT_PATH="${BASH_SOURCE[0]}";
if([ -h "${SCRIPT_PATH}" ]) then
  while([ -h "${SCRIPT_PATH}" ]) do SCRIPT_PATH=`readlink "${SCRIPT_PATH}"`; done
fi
pushd . > /dev/null
cd `dirname ${SCRIPT_PATH}` > /dev/null
SCRIPT_PATH=`pwd`;
popd  > /dev/null

#set our environment
export RCDB_HOME=$SCRIPT_PATH 
export LD_LIBRARY_PATH="$RCDB_HOME/cpp/lib":$LD_LIBRARY_PATH
export CPLUS_INCLUDE_PATH="$RCDB_HOME/cpp/include":$CPLUS_INCLUDE_PATH
export PYTHONPATH="$RCDB_HOME/python":$PYTHONPATH
export PATH="$RCDB_HOME":"$RCDB_HOME/cpp/bin":$PATH


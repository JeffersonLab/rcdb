import os
import sys
import inspect

#  === CONFIG ===

# The path to main rcdb folder. It is the folder, 
# where 'python', 'rcdb_www' and 'sql' subfolders are located 
#rcdb_home = '/home/romanov/rcdb/rcdb'

#determine rcdb_home automatically assuming that this wsgi file is in 
# $RCDB_HOME/rcdb_www directory
rcdb_home = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
rcdb_home = os.path.join(rcdb_home,"..")



#add rcdb python folder to the path
rcdb_python_folder = os.path.join(rcdb_home, "python")
if rcdb_python_folder not in sys.path:
	sys.path.insert(0, rcdb_python_folder)

#add rcdb_www module add folder to the path 
if rcdb_home not in sys.path:
	sys.path.insert(0, rcdb_home)

#set connection string
import rcdb_www


def application(environ, start_response):
    if "RCDB_CONNECTION" in environ.keys():
        rcdb_www.app.config["SQL_CONNECTION_STRING"] = environ["RCDB_CONNECTION"]
    return rcdb_www.app(environ, start_response)
    
#give an application for apache
#from rcdb_www import app as application

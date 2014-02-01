#
import os, sys, inspect

    #sys.path.insert(0, cmd_folder)

if __name__ == '__main__':

    #add trigger db library if needed
    this_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
    python_folder = os.path.join(this_folder, "python")
    if python_folder not in sys.path:
        sys.path.insert(0, python_folder)

    #import and start web site
    import tridb_www
    tridb_www.app.run()

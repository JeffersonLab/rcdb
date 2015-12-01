import os
import sys
import inspect


def get_this_folder():
    """Returns the folder of

    """

if __name__ == '__main__':

    # add trigger db library if needed
    this_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
    python_folder = os.path.join(this_folder, "python")
    if python_folder not in sys.path:
        sys.path.insert(0, python_folder)

    # import and start web site
    import rcdb_www

    if "RCDB_CONNECTION" in os.environ.keys():
        rcdb_www.app.config["SQL_CONNECTION_STRING"] = os.environ["RCDB_CONNECTION"]

    rcdb_www.app.run()

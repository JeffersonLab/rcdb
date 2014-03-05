import runconf_db


if __name__ == '__main__':

    #create API and connect to DB
    db = runconf_db.ConfigurationProvider()
    db.connect("mysql+mysqlconnector://runconf_db@127.0.0.1/runconf_db")

    #get run configuration for run #1
    run = db.obtain_run_configuration(1)

    db.add_configuration_file(1, "sasha1.py")



import trigger_db


if __name__ == '__main__':

    #create API and connect to DB
    db = trigger_db.ConfigurationProvider()
    db.connect("mysql+mysqlconnector://trigger_db@127.0.0.1/trigger_db")

    #get run configuration for run #1
    run = db.obtain_run_configuration(1)

    db.add_configuration_file(1, "sasha1.py")



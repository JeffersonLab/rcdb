import logging
import sys
import runconf_db
import datetime

#setup logger
log = logging.getLogger('rcdb')  # create run configuration standard logger
log.addHandler(logging.StreamHandler(sys.stdout))  # add console output for logger
log.setLevel(logging.DEBUG)  # print everything. Change to logging.INFO for less output

if __name__ == '__main__':
    #times
    dt_run1_start = datetime.datetime(2014, 03, 04, 14, 10)
    dt_run1_end = dt_run1_start + datetime.timedelta(minutes=50, seconds=56)
    dt_run2_start = dt_run1_start + datetime.timedelta(hours=1)
    dt_run2_end = dt_run2_start + datetime.timedelta(minutes=30, seconds=21)
    dt_run3_start = dt_run2_start + datetime.timedelta(hours=1)
    dt_run3_end = dt_run3_start + datetime.timedelta(minutes=40)
    dt_run4_start = dt_run3_start + datetime.timedelta(hours=25)
    dt_run4_end = dt_run4_start + datetime.timedelta(minutes=20)

    #create API and connect to DB
    db = runconf_db.ConfigurationProvider()
    db.connect("mysql+mysqlconnector://runconf_db@127.0.0.1/runconf_db")

    boards = [db.obtain_board(runconf_db.FADC250_KEY, "CRXFADC1001"),
              db.obtain_board(runconf_db.FADC250_KEY, "CRXFADC1002"),
              db.obtain_board(runconf_db.FADC250_KEY, "CRXFADC1003"),
              db.obtain_board(runconf_db.FADC250_KEY, "CRXFADC1004"),
              db.obtain_board(runconf_db.FADC250_KEY, "CRXFADC1005"),
              db.obtain_board(runconf_db.FADC250_KEY, "CRXFADC1006")]

    roc1 = db.obtain_crate("ROC1")
    roc2 = db.obtain_crate("ROC2")

    # --------------------------------------------------------------------------------------
    #            R U N   1
    #---------------------------------------------------------------------------------------
    #get run configuration for run #1
    #run = db.obtain_run_configuration(1)
    db.add_run_start_time(1, dt_run1_start)
    db.add_run_record(1,
                      runconf_db.START_COMMENT_RECORD_KEY,
                      "This is 1-st run generated as example by runconf_db software test",
                      dt_run1_start)

    db.add_configuration_file(1, "prestart_example.xml")
    db.add_configuration_file(1, "fadc250_example1.cnf")
    db.add_configuration_file(1, "fadc250_example2.cnf")

    db.add_board_installation_to_run(1, (roc1, boards[0], 2))
    db.add_board_installation_to_run(1, (roc1, boards[1], 3))
    db.add_board_installation_to_run(1, (roc1, boards[2], 8))
    db.add_board_installation_to_run(1, (roc1, boards[3], 9))
    db.add_board_installation_to_run(1, (roc2, boards[4], 7))
    db.add_board_installation_to_run(1, (roc2, boards[5], 9))

    dac_values = [0, 1, 2, 3, 3, 2, 1, 0, 4, 5, 6, 7, 7, 6, 5, 4]

    for i, board in enumerate(boards):
        unique_values = [dac_value + i for dac_value in dac_values]
        dac_preset = db.obtain_dac_preset(board, unique_values)
        db.add_board_config_to_run(1, board, dac_preset)


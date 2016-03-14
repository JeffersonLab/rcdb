import rcdb
from rcdb import Board
from rcdb import BoardConfiguration
from rcdb import RunConfiguration

#define a function that prints information about run
def print_run_information(run):
    """
    function that prints information about one run
    run is given as RunConfiguration object

    :param run: RunConfiguration
    :type run: RunConfiguration
    :return: None
    """
    assert (isinstance(run, RunConfiguration))

    print
    print("------------------------")
    print("run number: '{0}'   db_id: '{1}' ".format(run.number, run.id))
    print("boards configurations:")
    for board_config in run.board_configs:
        assert (isinstance(board_config, BoardConfiguration))
        print("   name: '{0}'  crait: '{1}'  slot: '{2}' threshold_preset_version: {3}  values: '{4}'".format(
            board_config.board.board_name,
            board_config.crait,
            board_config.slot,
            board_config.threshold_preset.version,
            board_config.threshold_preset.values
        ))


db = rcdb.connect()

#select all runs we have
runs = db.query(RunConfiguration).all()

#print information about each run
print("runs information:")
for run in runs:
    print_run_information(run)



# To create a new run, what do we need?
# 1) What boards?
# 2) What is crait and slot for each board
# 3) What are threshold values for each board
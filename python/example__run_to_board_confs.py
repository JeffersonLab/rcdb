import trigger_db
from trigger_db import Board
from trigger_db import BoardConfiguration
from trigger_db import RunConfiguration

db = trigger_db.connect()

#select all runs we have
runs = db.query(RunConfiguration).all()

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
    print()
    print("------------------------")
    print("run number: '{0}'   db_id: '{1}' ".format(run.number, run.id))
    print("boards configurations:")
    for board_config in run.board_configs:
        assert (isinstance(board_config, BoardConfiguration))
        print("   name: '{0}'  crait: '{1}'  slot: '{2}'".format(
            board_config.board.board_name,
            board_config.crait,
            board_config.slot))

#print information about each run
print("run numbers:")
for run in runs:
    print_run_information(run)

#check that there is no changing objects
print(db.new)

# To create a new run, what do we need?
# 1) What boards?
# 2) What is crait and slot for each board
# 3) What are threshold values for each board
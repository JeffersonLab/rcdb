
import trigger_db
from trigger_db import Board
from trigger_db import ThresholdPreset

db = trigger_db.connect()

boards = db.query(Board).all()

for board in boards:
    print(board)
    print("Type {0} Name {1}".format(board.board_type, board.board_name))

print("===================")

boards = db.query(Board).filter(Board.board_type=="FADC").all()

for board in boards:
    print(board)
    print("Type {0} Name {1}".format(board.board_type, board.board_name))
print("===================")


board = db.query(Board).filter(Board.id == 1).one()
print(board.board_name)
print(board.threshold_presets)

for preset in board.threshold_presets:
    print(preset.version, preset.values)

print("===================")

#preset = ThresholdPreset()
#preset.values = [6,6,6,6,6,6,6,6,6,6,6,6,6]
#board.threshold_presets.append(preset)
#db.commit()








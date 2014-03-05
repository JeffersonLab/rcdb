__author__ = 'DmitryRa'

import runconf_db
from runconf_db import Board           #Board class represents each physical board
from runconf_db import ThresholdPreset #Threshold values


db = runconf_db.connect()
boards = db.query(Board).all()
print(boards)

print(db.dirty)
print(db.new)


#save changes to db
#db.commit()




































"""
boards = db.query(Board).filter(Board.board_type=="FADC").all()
print(boards)

for board in boards:
    print(board.name)
    print(len(board.threshold_presets))
    print(board.threshold_presets[0].values)

th = ThresholdPreset()
board = boards[0]
board.threshold_presets.append(th)
#th.board = boards[0]
th.values = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]


db.add(th)
print(db.dirty)
db.commit()"""
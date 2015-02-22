import rcdb
from rcdb.model import Run


db = rcdb.connect()

boards = db.query(Board).all()


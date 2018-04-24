import sys, tempfile, os
from subprocess import call
import rcdb
from rcdb.model import ConditionType, Condition, Run

if len(sys.argv) < 3:
    print "edit_run_comment.py [password] [run]"
    sys.exit(0)

passwd = sys.argv[1]
run = sys.argv[2]

EDITOR = os.environ.get('EDITOR','nano')

# get the current comment from RCDB
try:
    db = rcdb.RCDBProvider("mysql://rcdb:%s@gluondb1/rcdb"%sys.argv[1])
    initial_message =  db.get_condition(run,"user_comment").value
except Exception as e:
    print "Problems accessing RCDB!"
    print e
    sys.exit(0)

with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
    tf.write(initial_message)
    tf.flush()
    call([EDITOR, tf.name])

    # do the parsing with `tf` using regular File operations.
    # for instance:
    tf.seek(0)
    edited_message = tf.read()

    # update RCDB
    db.add_condition(run, "user_comment", edited_message, True)

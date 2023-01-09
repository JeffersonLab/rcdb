import sys
import rcdb
from rcdb.model import ConditionType, Run, Condition


def print_usage():
    print("""
    Removes comments like:
    Run type:: COSMIC_raw Config:: TRG_COSMIC_BCAL_raw_b1.conf CONFIG FILE:: /home/hdops/CDAQ/daq_dev_v0.31/daq/config/hd_all/TRG_COSMIC_BCAL_raw_b1.conf (Re)Created:: on Tue Dec 8 15:54:07 EST 2015

    Usage:
        python replace_comments.py <connection-string>

    """)


def remove_comments(con_str):
    """

    :param con_str: DB connection string
    :return:
    """
    db = rcdb.RCDBProvider(con_str)
    comment_type = db.get_condition_type("user_comment")

    results = db.session.query(Condition).join(Condition.type)\
        .filter(Condition.type == comment_type)\
        .filter(Condition.text_value.like('%CONFIG FILE%')).all()

    for result in results:
        print(result)
        result.text_value = ""

    db.session.commit()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_usage()
    else:
        remove_comments(sys.argv[1])



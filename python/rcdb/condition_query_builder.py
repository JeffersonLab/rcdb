from sqlalchemy.orm.query import Query
from rcdb import RCDBProvider


class ConditionQueryBuilder(object):

    gt=[".gt.", ">"]
    ge=[".ge.", ">="]
    lt=[".lt.", "<"]
    le=[".le.", "<="]
    eq=[".eq.", "=="]
    ne=[".ne.", "!="]

    def build_query(self, db, query, entities):
        """

        :param query:
        :type query: query
        :param entities:
        :return:
        """
        assert isinstance(query, Query)
        assert isinstance(db, RCDBProvider)

        comparator = None

        for name, operator, value in entities:
            ct = db.get_condition_type(name)




    


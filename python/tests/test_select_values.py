import unittest

import rcdb
import rcdb.model
from rcdb.model import Run, ConditionType
from rcdb.provider import destroy_all_create_schema


class TestRun(unittest.TestCase):
    """ Tests ConditionType, ConditionValue classes and their operations in provider"""

    def setUp(self):
        self.db = rcdb.RCDBProvider("sqlite://", check_version=False)
        destroy_all_create_schema(self.db)
        runs = {}
        # create runs
        for i in range(1, 6):
            runs[i] = self.db.create_run(i)

        runs[9] = self.db.create_run(9)
        self.runs = runs

        self.db.create_condition_type("a", ConditionType.INT_FIELD, "Test condition 'a'")
        self.db.create_condition_type("b", ConditionType.FLOAT_FIELD, "Test condition 'b'")
        self.db.create_condition_type("c", ConditionType.BOOL_FIELD, "Test condition 'v'")
        self.db.create_condition_type("d", ConditionType.STRING_FIELD, "Test condition 'd'")
        self.db.create_condition_type("e", ConditionType.JSON_FIELD, "Test condition 'e'")
        self.db.create_condition_type("f", ConditionType.STRING_FIELD, "Test condition 'f'")
        self.db.create_condition_type("g", ConditionType.BLOB_FIELD, "Test condition 'g'")

        # create conditions
        self.db.add_condition(1, "a", 1)
        self.db.add_condition(2, "a", 2)
        self.db.add_condition(3, "a", 3)
        self.db.add_condition(4, "a", 4)
        self.db.add_condition(9, "a", 9)

        self.db.add_condition(1, "b", 1.01)
        self.db.add_condition(2, "b", 7.0/3.0)
        self.db.add_condition(3, "b", 2.55)
        self.db.add_condition(4, "b", 1.64)
        self.db.add_condition(5, "b", 2.32)
        self.db.add_condition(9, "b", 2.02)

        self.db.add_condition(1, "c", False)
        self.db.add_condition(2, "c", True)
        self.db.add_condition(3, "c", True)
        self.db.add_condition(4, "c", True)
        self.db.add_condition(5, "c", False)
        self.db.add_condition(9, "c", True)

        self.db.add_condition(1, "d", "haha")
        self.db.add_condition(4, "d", "hoho")
        self.db.add_condition(5, "d", "bang")
        self.db.add_condition(9, "d", "mew")

        self.db.add_condition(1, "e", '{"a":1}')
        self.db.add_condition(4, "e", "[1,2,3]")
        self.db.add_condition(9, "e", '[3,2,{"b":5}]')

        self.db.add_condition(4, "f", "my only value")

        self.db.add_condition(5, "g", "aGVsbG8gd29ybGQ=")

        """
        run |     a     |     b     |     c     |      d     |     e         |     f         |     g  
        -----------------------------------------------------------------------------------------------------   
          1 | 1         | 1.01      | False     | haha       | {"a":1}       | None          | None   
          2 | 2         | 2.333...  | True      | None       | None          | None          | None   
          3 | 3         | 2.55      | True      | None       | None          | None          | None   
          4 | 4         | 1.64      | True      | hoho       | [1,2,3]       | my only value | None 
          5 | None      | 2.32      | False     | bang       | None          | None          | aGVsbG8gd29ybGQ=   
          9 | 9         | 2.02      | True      | mew        | [3,2,{"b":5}] | None          | None   

        """

    def tearDown(self):
        self.db.disconnect()

    def test_select_values(self):
        """Test of Run in db function"""
        result = self.db.select_values(['c', 'd', 'f'], "a in [1,2,4,9] and b > 2", run_min=2)

        """
        run |     a     |     b     |     c     |      d     |     e         |     f         |     g  
        -----------------------------------------------------------------------------------------------------
          2 | 2         | 2.333...  | True      | None       | None          | None          | None
          9 | 9         | 2.02      | True      | mew        | [3,2,{"b":5}] | None          | None   

        """

        self.assertEqual(result.rows, [[2, True, None, None], [9, True, u'mew', None]])

    def test_select_values_no_filter(self):
        """Test of Run in db function"""
        result = self.db.select_values(['a', 'd'], run_min=4)
        self.assertEqual(result.rows, [[4, 4, u'hoho'], [5, None, u'bang'], [9, 9, u'mew']])

    def test_select_values_no_filter(self):
        """Test of Run in db function"""
        result = self.db.select_values(['a', 'd'], run_min=4, insert_run_number=False)
        self.assertEqual(result.rows, [[4, u'hoho'], [None, u'bang'], [9, u'mew']])

    def test_select_values_desc_order(self):
        """Test of Run in db function"""
        result = self.db.select_values(['a', 'd'], run_min=4, insert_run_number=False, sort_desc=True)
        self.assertEqual(result.rows, [[9, u'mew'], [None, u'bang'], [4, u'hoho']])

    def test_select_values_by_run(self):
        """Test of Run in db function"""
        result = self.db.select_values(['a', 'd'], runs=[9, self.db.get_run(4)], insert_run_number=False)
        self.assertEqual(result.rows, [[4, u'hoho'], [9, u'mew']])











import unittest

import rcdb
import rcdb.model
from rcdb.model import Run, ConditionType


class TestRun(unittest.TestCase):
    """ Tests ConditionType, ConditionValue classes and their operations in provider"""

    def setUp(self):
        """
        run |     a     |     b     |     c     |      d     |     e         |     f
        -------------------------------------------------------------------------------------
          1 | 1         | 1.01      | False     | haha       | {"a":1}       | None
          2 | 2         | 2.54      | True      | None       | None          | None
          3 | 3         | 2.55      | True      | None       | None          | None
          4 | 4         | 1.64      | True      | hoho       | [1,2,3]       | my only value
          5 | None      | 2.32      | False     | bang       | None          | None
          9 | 9         | 2.02      | True      | mew        | [3,2,{"b":5}] | None

        """

        self.db = rcdb.RCDBProvider("sqlite://", check_version=False)
        rcdb.provider.destroy_all_create_schema(self.db)
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

        self.db.add_condition(1, "a", 1)
        self.db.add_condition(2, "a", 2)
        self.db.add_condition(3, "a", 3)
        self.db.add_condition(4, "a", 4)
        self.db.add_condition(9, "a", 9)

        self.db.add_condition(1, "b", 1.01)
        self.db.add_condition(2, "b", 2.54)
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

    def tearDown(self):
        self.db.disconnect()

    def test_select_runs(self):
        """Test of Run in db function"""
        result = self.db.select_runs("a in [1,2,4,9] and b > 2", run_min=2)
        self.assertEqual(result.runs, [self.runs[2], self.runs[9]])
        self.assertEqual(result.filter_condition_names, ['a', 'b'])

    def test_select_no_query(self):
        result = self.db.select_runs(run_min=4, run_max=9)
        self.assertEqual(result.runs, [self.runs[4], self.runs[5], self.runs[9]])
        self.assertEqual(result.filter_condition_names, [])

    def test_selection_result(self):
        """Using result object as list"""
        result = self.db.select_runs("c")
        test_array = [run for run in result]
        self.assertEqual(result.runs, test_array)
        self.assertEqual(result[0].number, 2)

    def test_selection_get_values(self):
        """Test getting values from selected runs"""

        # 1. Without run numbers
        rows = self.db.select_runs(run_min=3, run_max=5).get_values(['e', 'a', 'd'])
        awaited_rows = [[None, 3, None],
                        ['[1,2,3]', 4, 'hoho'],
                        [None, None, 'bang']]
        self.assertEqual(rows, awaited_rows)

        # 2. With run numbers
        rows = self.db.select_runs(run_min=3, run_max=5).get_values(['e', 'a', 'd'], insert_run_number=True)
        awaited_rows = [[3, None, 3, None],
                        [4, '[1,2,3]', 4, 'hoho'],
                        [5, None, None, 'bang']]
        self.assertEqual(rows, awaited_rows)

        # 3. Only one field
        rows = self.db.select_runs(run_min=3, run_max=5).get_values('e')
        awaited_rows = [[None], ['[1,2,3]'], [None]]
        self.assertEqual(rows, awaited_rows)

    def test_selection_get_values_bad(self):
        """Test extreme conditions for get_values"""

        # 1. No runs selected
        rows = self.db.select_runs(run_min=10, run_max=15).get_values(['e', 'a', 'd'])
        awaited_rows = [[]]
        self.assertEqual(rows, awaited_rows)

        # 2. Only one run selected
        rows = self.db.select_runs(run_min=9).get_values(['f', 'a'])
        awaited_rows = [[None, 9]]
        self.assertEqual(rows, awaited_rows)

        # 3. No conditions given
        rows = self.db.select_runs(run_min=5).get_values([])
        awaited_rows = [[], []]
        self.assertEqual(rows, awaited_rows)

        # 4. No conditions given, but run numbers should be there
        rows = self.db.select_runs(run_min=5).get_values([], insert_run_number=True)
        awaited_rows = [[5], [9]]
        self.assertEqual(rows, awaited_rows)

        # 5. Emty values in the end
        rows = self.db.select_runs(run_min=3).get_values('f')
        awaited_rows = [[None], ['my only value'], [None], [None]]
        self.assertEqual(rows, awaited_rows)

    def test_select_runs_sort_order(self):
        """Test sort_desc parameter"""
        result = self.db.select_runs("a>0", sort_desc=True)
        run_numbers = [run.number for run in result.runs]
        awaited_run_numbers = [9, 4, 3, 2, 1]
        self.assertEqual(run_numbers, awaited_run_numbers)

        result = self.db.select_runs(run_min=3, run_max=5, sort_desc=True)
        run_numbers = [run.number for run in result.runs]
        awaited_run_numbers = [5, 4, 3]
        self.assertEqual(run_numbers, awaited_run_numbers)

    def test_get_values_order_desc(self):
        """Test getting values in descending order"""

        rows = self.db.select_runs(run_min=3, run_max=5, sort_desc=True).get_values(['e', 'a', 'd'], True)
        awaited_rows = [[5, None, None, 'bang'],
                        [4, '[1,2,3]', 4, 'hoho'],
                        [3, None, 3, None],
                        ]
        self.assertEqual(rows, awaited_rows)









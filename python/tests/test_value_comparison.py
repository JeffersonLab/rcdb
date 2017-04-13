import unittest
import rcdb
import rcdb.model
from rcdb.model import ConditionType


class TestValueComparison(unittest.TestCase):
    """ Tests ConditionType, ConditionValue classes and their operations in provider"""

    def setUp(self):
        self.db = rcdb.RCDBProvider("sqlite://", check_version=False)
        rcdb.provider.destroy_all_create_schema(self.db)
        # create run
        self.db.create_run(1)

    def tearDown(self):
        self.db.disconnect()

    def test_values_are_equal(self):
        """Test of create_condition_type function"""

        # Create condition type
        ctf = self.db.create_condition_type("test_float", ConditionType.FLOAT_FIELD, "This is a test")
        cti = self.db.create_condition_type("test_int", ConditionType.INT_FIELD, "This is a test")
        cts = self.db.create_condition_type("test_string", ConditionType.STRING_FIELD, "This is a test")

        self.assertFalse(cts.values_are_equal("ha", "ra"))
        self.assertTrue(cts.values_are_equal("xx", "xx"))

        self.assertTrue(ctf.values_are_equal(3.14, 3.14))
        self.assertTrue(ctf.values_are_equal(3.0, 3))
        self.assertTrue(ctf.values_are_equal(3.14, "3.14"))
        self.assertFalse(ctf.values_are_equal(3.15, "3.14"))

        self.assertTrue(ctf.values_are_equal(3, 3))

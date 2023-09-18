import unittest

import rcdb
import rcdb.model
from rcdb.model import SchemaVersion


class TestSqlSchemaVersion(unittest.TestCase):
    """ Tests the Sql Schema version work"""

    def setUp(self):
        self.db = rcdb.RCDBProvider("sqlite://", check_version=False)

    def tearDown(self):
        self.db.disconnect()

    def test_right_schema_version(self):
        """Test of Run in db function"""
        rcdb.model.Base.metadata.create_all(self.db.engine)
        v = SchemaVersion()
        v.version = rcdb.SQL_SCHEMA_VERSION
        self.db.session.add(v)

        v = SchemaVersion()
        v.version = rcdb.SQL_SCHEMA_VERSION - 1
        self.db.session.add(v)
        self.db.session.commit()

        self.assertEqual(self.db.get_schema_version(), rcdb.SQL_SCHEMA_VERSION)

    def test_no_schema_version(self):
        """Test of Run in db function"""

        def should_raise():
            rcdb.RCDBProvider("sqlite://", check_version=True)

        self.assertRaises(Exception, should_raise)

    def test_lower_schema_version(self):
        """Checks that lower schema version wouldn't work"""

        rcdb.model.Base.metadata.create_all(self.db.engine)
        v = SchemaVersion()
        v.version = 0
        self.db.session.add(v)
        self.db.session.commit()
        self.assertFalse(self.db.get_schema_version())






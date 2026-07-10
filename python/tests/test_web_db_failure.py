"""Web DB-failure handling.

A database selected in the navbar (stored in the ``rcdb_database`` cookie) may
be unreachable or access-denied server-side (e.g. the MariaDB ``rcdb`` user has
no GRANT on ``xem2``/``pionct`` -> pymysql ``(1044, "Access denied ...")``).

These tests pin the required behaviour:

* such a failure renders a graceful page (top menu + DB selector + a red
  "DB connection failure" strip), never a raw 500;
* no sensitive detail (connection string, host, user, error code/text) leaks
  into the page, while the full exception is written to the application log;
* the failure is not sticky -- reloading after the DB recovers, or switching to
  a working DB, renders normally with no poisoned cookie or cached engine.
"""

import unittest

from sqlalchemy.exc import OperationalError

import rcdb
import rcdb.provider
import rcdb.web


class TestWebDbFailure(unittest.TestCase):
    def setUp(self):
        self.app = rcdb.web.app
        self.app.testing = True

        # Save config we mutate so other tests see the app untouched.
        self._saved = {k: self.app.config.get(k) for k in
                       ("AVAILABLE_DATABASES", "DEFAULT_DATABASE")}
        self.app.config["AVAILABLE_DATABASES"] = {
            "good": "sqlite:///good",
            "bad": "sqlite:///bad",
        }
        self.app.config["DEFAULT_DATABASE"] = "sqlite:///good"

        self.client = self.app.test_client()

        # Replace connect(): raise an access-denied-style OperationalError for the
        # "bad" DB (while it is "down"); connect a fresh in-memory schema for the
        # "good" one. ``bad_down`` flips to False to simulate recovery.
        self.bad_down = True
        self._orig_connect = rcdb.ConfigurationProvider.connect
        test = self

        def fake_connect(provider, connection_string="", check_version=True):
            if "bad" in connection_string and test.bad_down:
                raise OperationalError(
                    "SELECT 1", {},
                    Exception("(1044, \"Access denied for user 'rcdb'@'%' "
                              "to database 'bad'\")"))
            test._orig_connect(provider, "sqlite://", check_version=False)
            rcdb.provider.destroy_all_create_schema(provider)

        rcdb.ConfigurationProvider.connect = fake_connect

    def tearDown(self):
        rcdb.ConfigurationProvider.connect = self._orig_connect
        for k, v in self._saved.items():
            if v is None:
                self.app.config.pop(k, None)
            else:
                self.app.config[k] = v

    def _get(self, path="/", db=None):
        # Fresh client per call so the cookie jar carries only what we set here
        # (the Werkzeug test client ignores a raw Cookie header, hence set_cookie).
        client = self.app.test_client()
        if db:
            client.set_cookie("rcdb_database", db)
        return client.get(path)

    def test_failure_renders_graceful_page_not_500(self):
        with self.assertLogs("rcdb.web", level="ERROR") as cm:
            resp = self._get("/", db="bad")

        # Graceful, retryable status -- never a raw 500.
        self.assertEqual(resp.status_code, 503)
        self.assertNotEqual(resp.status_code, 500)

        body = resp.get_data(as_text=True)
        # Red strip + intact top menu incl. the DB selector to switch away.
        self.assertIn("DB connection failure", body)
        self.assertIn('id="dbSelector"', body)
        self.assertIn(">bad<", body)
        self.assertIn(">good<", body)

        # No sensitive detail leaks into the page ...
        for secret in ("1044", "Access denied", "sqlite:///bad", "rcdb@",
                       "OperationalError", "Traceback"):
            self.assertNotIn(secret, body)

        # ... but the log has the full picture (db name + underlying error).
        logtext = "\n".join(cm.output)
        self.assertIn("bad", logtext)
        self.assertIn("1044", logtext)

    def test_reload_recovers_after_db_comes_back(self):
        # Same cookie, DB down -> graceful 503.
        self.assertEqual(self._get("/", db="bad").status_code, 503)

        # DB recovers; a plain reload (identical cookie) must render normally.
        self.bad_down = False
        resp = self._get("/", db="bad")
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("DB connection failure", resp.get_data(as_text=True))

    def test_switching_to_working_db_recovers(self):
        self.assertEqual(self._get("/", db="bad").status_code, 503)
        resp = self._get("/", db="good")
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("DB connection failure", resp.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()

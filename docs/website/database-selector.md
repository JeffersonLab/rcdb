# Multi-Database Selector

The RCDB web interface supports switching between multiple databases from the browser.
When configured, a dropdown selector appears in the navbar allowing users to pick a database.
The selection is saved in a cookie and persists across sessions.

### How It Works

- The Flask app has two config keys: `AVAILABLE_DATABASES` (a dict of `name -> connection_string`)
  and `DEFAULT_DATABASE` (the connection string to use when no cookie is set).
- On each request, `before_request()` checks `AVAILABLE_DATABASES`. If non-empty, it reads the
  `rcdb_database` cookie to determine which database to connect to.
- If the cookie is missing or invalid, it falls back to `DEFAULT_DATABASE`. If `DEFAULT_DATABASE`
  is not in the available list, it logs a warning and uses the first entry.
- When `AVAILABLE_DATABASES` is empty (the default), all behavior is identical to a single-database setup.


## CLI (`rcdb web`)

Use the `--add-db` flag (repeatable) to register named databases:

```bash
rcdb -c mysql+pymysql://rcdb@prodhost/rcdb web \
    --add-db "Production=mysql+pymysql://rcdb@prodhost/rcdb" \
    --add-db "Test=mysql+pymysql://rcdb@testhost/rcdb_test"
```

- Each `--add-db` value has the format `NAME=CONNECTION_STRING`.
- The `-c` / `--connection` / `RCDB_CONNECTION` value becomes the default database.
- If no `-c` is provided, the first `--add-db` entry is used as the default.


## Server Configuration

### WSGI

Set the config keys directly in the WSGI script:

```python
import rcdb.web

rcdb.web.app.config["AVAILABLE_DATABASES"] = {
    "Production": "mysql+pymysql://rcdb@prodhost/rcdb",
    "Test": "mysql+pymysql://rcdb@testhost/rcdb_test",
}
rcdb.web.app.config["DEFAULT_DATABASE"] = "mysql+pymysql://rcdb@prodhost/rcdb"

application = rcdb.web.app
```

When `AVAILABLE_DATABASES` is set, the `SQL_CONNECTION_STRING` key is not used
for connection selection (though it should still be set as a fallback).

## UI Behavior

The selector appears to the left of the "Run or min-max" search box in the navbar.
Each option shows the database name and a connection hint (e.g. `Production (rcdb@prodhost)`).

When the user selects a different database:

1. A cookie `rcdb_database` is set (1-year expiry, `SameSite=Lax`).
2. The current page reloads, now connected to the selected database.

## Key Files

| File | Role |
|------|------|
| `python/rcdb/web/__init__.py` | Config defaults, `before_request()` logic, `_connection_hint()` helper |
| `python/rcdb/web/templates/layouts/base.html` | Navbar `<select>` element and JS cookie handler |
| `python/rcdb/cli/web.py` | `--add-db` CLI option parsing |

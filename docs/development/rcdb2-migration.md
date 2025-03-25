# RCDB 2.0 – What Changed?

1. **Python 2 to 3**
    - **Python 3.9+** (or at least 3.8) is now required. Python 2.x is no longer supported.
      RCDB now will follow [official supported python versions](https://devguide.python.org/versions/)  
    - Some code that used to be Python 2 or Python <3.8–compatible is removed.
    - Legacy utilities and examples are removed   

2. **Dependencies**
    - RCDB is now distributed in a way that expects standard Python packages to be installed via `pip` 
      or system packages (e.g. `pymysql`, `flask`, `click`, `sqlalchemy>=2`, etc.).
    - Previously, RCDB might have shipped more dependencies internally or supported older versions. 
      Now, you must ensure the needed packages are installed system-wide or in a virtual environment.

3. **Schema Version & Tables**
    - The database schema changed which is the main driver of backward incompatibilities. 
      The new code checks that your DB schema is at least at version 2.       
    - New tables have been introduced, such as `run_periods` (for grouping runs) and `alias` (for query aliases), plus changes to the existing `conditions` and `condition_types` tables.
    - In v2, there is an official `SchemaVersion` model/table that is used to store the current schema version and a comment.

4. **Website / Flask App**
    - The built-in Flask-based website is now part of RCDB and can be launched via `rcdb web`. 
    - Apache/WSGI usage is simpler in principle, but you must point the WSGI script to the `rcdb.web.app`. 
      Also ensure environment variables or config are set so that `rcdb.web.app.config["SQL_CONNECTION_STRING"]` knows where your DB is.

5. **Installation & CLI**
    - The recommended installation method is now a standard “pip install” from source or from PyPI.
    - You can invoke all the CLI commands via `rcdb ...` (e.g. `rcdb db init`, `rcdb db update`, `rcdb select ...`, `rcdb web`, etc.).
    - Additional subcommands exist in v2 (e.g. `rcdb rp` for Run Periods, `rcdb repair` commands, etc.).
    - `rcnd` command is there for compatibility but is considered obsolete

6. **Backwards Incompatibilities**
    - The DB schema is not directly backwards-compatible. 
      Old RCDB1 code will fail to read a newly migrated RCDB2 database. 
      Likewise, new RCDB2 code cannot run queries if the database is still at RCDB1 schema.
    - Old custom scripts that used Python 2 or the old method of “import rcdb; rcdb.XYZ()” 
      might need updates to Python 3 syntax and new function APIs.

---

# Migrating from RCDB 1 to RCDB 2


Because the schema has changed in RCDB 2.0, you **cannot** simply point the new RCDB code at the old DB. 
There is a built-in mechanism to attempt the migration, `rcdb db update` command.  
For production environments it is suggested to **clone** the database to something  
like `rcdb2` and applying updates to the new cloned DB.

**Recommended steps for RCDB2 upgrade**

- **Clone** your existing database (so you can preserve old data).
- **Install** RCDB 2.
- **Run** `rcdb db update` on the clone.
- **Validate** that everything looks correct.
- **Point** your new scripts and web interface at the updated DB.
- Optionally **retire** the old DB once you are sure no more RCDB1-based scripts need it.


1. **Back Up or Clone the Old Database**
    - Create a copy or replica of the existing RCDB1 database. For instance, if you had a database 
      named `rcdb` in MySQL, create a new schema named `rcdb2` and copy all data. 
    - This ensures the original DB remains intact and accessible to older scripts and software 
      that might still depend on it.

2. **Update / Initialize the New Database**
    - Point your `RCDB_CONNECTION` environment variable or your command-line `-c` argument to the **cloned** database (e.g. `mysql://rcdb@server/rcdb2`).
    - Use the RCDB CLI commands to **stamp** or **upgrade** the schema. For example:
      ```bash
      rcdb -c mysql://rcdb@server/rcdb2 db update
      ```
      or
      ```bash
      rcdb -c mysql://rcdb@server/rcdb2 db init --drop-all
      ```
      depending on your site’s approach.
    - The `db update` command attempts to detect an older schema, apply the new tables (`run_periods`, `alias`, etc.), and stamp the schema version as “2”. If your original DB was truly RCDB1, the built-in `update_v1` logic will create the new columns/tables needed.
    - Run `rcdb select ...`, `rcdb ls`, or `rcdb web` with the new `rcdb2` connection string to ensure queries function properly, conditions are intact, and the website can display data.
     
3. **Update DAQ scripts**
    - The most important part is that after DB update, one must update DAQ side that fill the database.
      RCDB2 is compatible enough for DAQ scripts to continue working if one updates python and installs dependencies.
    - Make sure you have Python 3.9+ (or 3.8 if tested). You can install dependencies by installing `rcdb` from pip:
      ```bash
      python -m pip install rcdb
      # Or if from source, python -m pip install .
      ```

4. **Update RCDB website**    
    - Update any environment variables, WSGI files, or scripts that reference the old database to point to your newly updated DB.
    - The simplest WSGI for the RCDB2:
    
      ```python
      import os
      import sys
      # add your project directory to the sys.path
      sys.path.insert(0, '/home/rcdb/rcdb_current/python')

      # import and start web site
      import rcdb.web
      rcdb.web.app.config["SQL_CONNECTION_STRING"] = os.environ["RCDB_CONNECTION"]
      application = rcdb.web.app
      ```

---

## Additional Notes

- If you never actually wrote data to RCDB1 (e.g., you only had a half-empty test DB), 
  it might be simpler to do a fresh `rcdb db init` with RCDB2.
- HallD, performed an RCDB1 → RCDB2 upgrade by creating an entirely “`rcdb2`” MySQL database, 
  updating it to rcdb2, then pointing new code to that database. 
  The old “`rcdb`” schema was retained for legacy purposes.




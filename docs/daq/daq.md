# DAQ 

## General concepts

RCDB is developed to be a general condition database to store this part of experimental "meta" data. 
While there are tools to integrate RCDB with CODA and EPICs, RCDB was never designed specifically for them.

There are several ideological ideas behind how RCDB works:

- **Minimum human interaction and alteration.**
  RCDB should be an automated database, which shall collect data as automatically as possible. 
  There are still several types of data usually provided by homo sapiens or similar 
  (run comments, for example). Still, the number of interactions with biological organisms should 
  be minimized.

- **Many updates during the run.**  
  RCDB is updated continuously throughout the run. 
  By default, RCDB does not maintain a history (though it has logs for other purposes). 
  Typically, the latest data is considered the most accurate, so newer data overwrites existing 
  values for the run. If it is necessary to preserve all values collected during the run, a JSON 
  array or collection should be incrementally saved as the run progresses. The experiment 
  can end unexpectedly due to hardware failure, software issues, or a human-issued abort command. 
  Updating and saving values continuously ensures that the most of the data is preserved 
  even if the system crashes.

- **Modularity.**
  There are usually several different aspects of what is being updated and how it is being updated. 
  For example, saving configuration files at the run start and creating the run, 
  periodically updating EPICS, making updates from CODA, and making updates from other software. 
  It is wise to organize scripts so that different aspects can be run independently 
  of each other or at least as independently as possible.

- **Modular responsibility.**
  Making things modular should allow parts to continue to work if one part fails. 
  And failing parts should be able to recover and not break things around. 
  At the same time, errors and recovery should never be silent. 
  We must report and log everything. Failures should be logged in great detail.

---

## Basic CODA–RCDB Integration Workflow

Below is an overview of how the Run Conditions Database (RCDB) integrates with 
CODA-based DAQ systems (particularly CODA3). We will highlight the main components, 
the workflow of how run information is obtained, and the guiding principles and modular 
responsibilities behind these processes.

### CODA (CEBAF Online Data Acquisition) Overview

CODA3 is a data-acquisition software from Jefferson Lab designed to manage run control for experiments. When you start, update, or end a run, CODA3 typically generates or updates a “run log” XML file containing essential information such as:
- Run number
- Start time, update time, end time
- Event count
- Run type, session, or configuration strings
- List of components and statistics (e.g., data rates per board)
- User comments written by shift workers

### RCDB Overview

The Run Conditions Database (RCDB) stores run-related information, or “conditions,” in a database (MySQL, SQLite, etc.). The *conditions* typically include:
- CODA-related items (e.g., event count, run start time)
- Slow controls data (EPICS, e.g., beam current, solenoid current, target status)
- Run configuration files, ROC configuration, or trigger settings
- User-provided run comments or statuses

RCDB is designed so that it can be updated multiple times per run and can hold the latest (i.e., “rightest”) known values.

### How the Data Flows

The core flow of CODA–RCDB integration looks like this:

1. **DAQ Transition Occurs (e.g., Start/Update/End)**  
   CODA triggers an update, creates or updates an XML log file with run info.

2. **Update Script is Invoked**
   - The `update.py` (or equivalent script) is typically run automatically by CODA or a cron/triggering mechanism.
   - It reads the CODA-generated log file (XML).

3. **Parsing the CODA File**
   - RCDB has a parser (e.g., `coda_parser.py`) that extracts the run number, times, event counts, etc.
   - If we are at run end, the parser obtains final totals; if at run start or update, partial information is recorded.

4. **Updating RCDB**
   - The script then calls various “update” modules (e.g., `update_coda.py`, `update_epics.py`, `update_run_config.py`, etc.) to insert or replace conditions in the database.
   - Slow controls data (EPICS) is also fetched—some or all of these modules can be selectively invoked, depending on command-line arguments or other configuration.

5. **Storing Conditions**
   - RCDB “conditions” for each run are stored in the database. Each condition can be updated multiple times if new data arrives (e.g., partial counters at run update).
   - RCDB overwrites the old value with the new, but if you want a time series (e.g., you want to store a changing quantity across the run), you can store it as an array or JSON object so that partial updates keep the data.

6. **Run Configuration Files**
   - Additional step: the scripts detect or are informed about relevant config files (trigger config, ROC config, .cnf files, etc.).
   - Those files can be archived in the RCDB as well, so that future analyses can see exactly which configuration was used for each run.

---

## Multiple Updates During the Run

One of the main RCDB design principles is that new run information often arrives *mid-run*, rather than only at the end. CODA3 can periodically update the run log file or produce partial messages about changes in rates or errors. The RCDB update scripts can be run multiple times:
- **Start** phase: Mark the run as started, log initial parameters.
- **Update** phase(s): Overwrite or update partial counters, slow controls, etc.
- **End** phase: Final event count, final times, final EPICS readbacks, etc.

By default, RCDB does not keep separate historical records of each partial update (the single “value” for a condition is overwritten). If you need a history, you typically store it inside a JSON field or keep an external logging system.


---

## Modular Responsibilities

RCDB code is structured into separate “update modules,” each with a clearly defined responsibility. Typical modules include:

1. **CODA Log Parser** (`coda_parser.py`, `update_coda.py`)
   - Extracts main CODA info: run number, event count, times, user comment, etc.
   - Saves them as conditions (`run_type`, `session`, `event_count`, etc.).

2. **Slow Controls / EPICS** (`update_epics.py`)
   - At run update or end, it calls EPICS queries (via `myStats`, `myData`, or `caget`) to fetch beam current, energies, solenoid current, target status, etc.
   - Stores them in the database as conditions.

3. **Run Configuration** (`update_run_config.py`)
   - HallD run configuration files or “main config” files are parsed to extract trigger equations, sub-system settings.
   - The script archives the config file in RCDB and sets conditions like `trigger_type`, `cdc_fadc125_mode`, etc.

4. **ROC Config** (`update_roc.py`)
   - If the main config references individual ROC config files, they are found, loaded, and archived in RCDB.

5. **Top-Level Script** (`update.py`)
   - Orchestrates the flow:
      1. Parse CODA file
      2. Possibly update RCDB for CODA conditions
      3. Possibly fetch EPICS data
      4. Possibly parse run config & ROC configs
   - Allows partial or full updates by specifying arguments (`--update=coda,epics,roc,config`) and reason (`start`, `update`, or `end`).

---

## Practical Example of an RCDB Update

Here is a simplified scenario to see how everything plugs together:

1. **Run Start**
   - CODA starts run #12345 and writes `current_run.log` with partial info.
   - `update.py current_run.log --reason=start --update=coda,config` is called automatically.
   - The script parses the run log → `run_number=12345`, sets `run_start_time`, “run_type,” etc., and archives the config file.
   - EPICS data might *not* be fetched yet unless we request it.

2. **Mid-Run**
   - CODA updates `current_run.log` with updated event count, or a cron job calls the script with `--reason=update`.
   - `update.py current_run.log --reason=update --update=epics` fetches slow controls data from EPICS, overwriting old beam current values in RCDB.

3. **Run End**
   - CODA finalizes the log with total events, end time, user comment.
   - `update.py current_run.log --reason=end --update=coda,epics` final parse.
   - RCDB is updated with final event count, final beam current, etc.

---

## Conclusions

By combining CODA’s capability to generate run log files with RCDB’s structured approach to storing “conditions,” users can automate the gathering of all relevant run metadata. Whether it is trigger settings, final event count, beam current from EPICS, or run config files, the system remains flexible, modular, and minimally reliant on manual data entry.

In short:

- **CODA** produces or updates an XML log.
- **RCDB** has scripts that parse logs, fetch slow controls, store everything as run conditions.
- **You can specify** which updates to run (`coda`, `epics`, `config`, `roc`) and at which transition (`start`, `update`, `end`).
- **Many updates** per run are allowed, overwriting conditions so that the latest entry is the final, official value.
- **Extra data** (like time-dependent EPICS readings) can be stored in JSON if you want a history across the run.

All of this ensures that you have a nearly complete “snapshot” of the run’s operational parameters in RCDB, ready for offline analysis and reference.

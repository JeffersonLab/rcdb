import sys
import click
from sqlalchemy import asc, desc

from rcdb.provider import RCDBProvider
from rcdb.model import ConfigurationFile, Run
from rcdb.cli.context import pass_rcdb_context


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _hash_str(value):
    """Normalize a stored sha256 to a printable string.

    The hash is stored base64-encoded and may come back from the DB as ``bytes``
    (SQLite) or ``str`` (other dialects), so we always render it as ``str``.
    """
    if isinstance(value, (bytes, bytearray)):
        return value.decode("ascii")
    return str(value)


def _resolve_run_range(db, run_min, run_max, run, run_period):
    """Resolve the run filter options into a (run_min, run_max) inclusive range.

    The three selection mechanisms are mutually exclusive:
      * ``--run-min`` / ``--run-max`` define a range (either side optional),
      * ``--run`` selects a single run,
      * ``--run-period`` selects a named run period.

    When nothing is given the full range ``(0, sys.maxsize)`` is returned, which
    means "all runs".
    """
    has_range = run_min is not None or run_max is not None
    has_run = run is not None
    has_period = run_period is not None

    if sum([has_range, has_run, has_period]) > 1:
        raise click.UsageError(
            "--run-min/--run-max, --run and --run-period are mutually exclusive; "
            "use only one of them.")

    if has_period:
        return _run_period_range(db, run_period)

    if has_run:
        return run, run

    lo = run_min if run_min is not None else 0
    hi = run_max if run_max is not None else sys.maxsize
    return lo, hi


def _run_period_range(db, name):
    """Resolve a run period *name* to a (run_min, run_max) range."""
    match = next((p for p in db.get_run_periods() if p.name == name), None)
    if match is None:
        raise click.UsageError("Run period '{}' is not found in DB.".format(name))
    return match.run_min, match.run_max


def _parse_run_spec(db, run_spec):
    """Parse a positional run specifier into a (run_min, run_max) range.

    The specifier is interpreted, in order:
      1. a single run number, e.g. ``1000``           -> (1000, 1000)
      2. a numeric run range, e.g. ``1000-2000``,     -> (1000, 2000)
         ``1000-`` -> (1000, maxsize), ``-2000`` -> (0, 2000)
      3. otherwise a run period name (which may itself contain '-').
    """
    spec = run_spec.strip()

    # 1) single run number
    if spec.isdigit():
        run = int(spec)
        return run, run

    # 2) numeric run range "lo-hi" (either side optional)
    if "-" in spec:
        lo_s, _, hi_s = spec.partition("-")
        lo_s, hi_s = lo_s.strip(), hi_s.strip()
        lo_ok = lo_s == "" or lo_s.isdigit()
        hi_ok = hi_s == "" or hi_s.isdigit()
        if lo_ok and hi_ok and (lo_s or hi_s):
            lo = int(lo_s) if lo_s else 0
            hi = int(hi_s) if hi_s else sys.maxsize
            return (lo, hi) if lo <= hi else (hi, lo)

    # 3) run period name
    return _run_period_range(db, spec)


# ---------------------------------------------------------------------------
# Group
# ---------------------------------------------------------------------------
@click.group("file", help="Inspect configuration/log files stored in the RCDB.")
@pass_rcdb_context
def file_command(context):
    """The 'file' group command. See subcommands like:

      rcdb file vers   - list all versions of a file
      rcdb file cat    - print the content of a file version
      rcdb file runs   - list per-run file versions for a file
      rcdb file ls     - list all files for a run / run period
      rcdb file search - find file names by substring
    """
    pass


# ---------------------------------------------------------------------------
# rcdb file vers <file name>
# ---------------------------------------------------------------------------
@file_command.command(name="vers", help="Show all versions of a file.")
@click.argument("file_name")
@pass_rcdb_context
def file_vers(context, file_name):
    """Show all versions (distinct content hashes) stored for FILE_NAME.

    Each row is printed as::

        <sha256 hash> - <last run number this version is used>

    Versions are sorted by their last used run number, descending.
    """
    db = context.require_connected_db()
    assert isinstance(db, RCDBProvider)

    files = db.session.query(ConfigurationFile) \
        .filter(ConfigurationFile.path == file_name) \
        .all()

    if not files:
        click.echo("No file '{}' found in DB.".format(file_name), err=True)
        raise click.Abort()

    rows = []
    for conf_file in files:
        run_numbers = [run.number for run in conf_file.runs]
        last_run = max(run_numbers) if run_numbers else None
        rows.append((_hash_str(conf_file.sha256), last_run))

    # Sort by last run descending; versions without runs (None) go last.
    rows.sort(key=lambda r: (r[1] is not None, r[1]), reverse=True)

    for sha256, last_run in rows:
        click.echo("{} - {}".format(sha256, last_run if last_run is not None else "none"))


# ---------------------------------------------------------------------------
# rcdb file cat <file name> [run] [--run=<run>] [--hash=<hash>]
# ---------------------------------------------------------------------------
@file_command.command(name="cat", help="Print the content of a file version.")
@click.argument("file_name")
@click.argument("run_arg", required=False, type=int)
@click.option("--run", "run_opt", type=int, default=None,
              help="Print the version of the file used in this run.")
@click.option("--hash", "file_hash", default=None,
              help="Print the version with this sha256 hash (a unique prefix is accepted).")
@pass_rcdb_context
def file_cat(context, file_name, run_arg, run_opt, file_hash):
    """Dump the raw content of a single version of FILE_NAME.

    The version is selected either by run (positional RUN or --run) or by
    --hash. Exactly one selector must be provided.

    Examples::

        rcdb file cat /path/coda.conf 1000
        rcdb file cat /path/coda.conf --run=1000
        rcdb file cat /path/coda.conf --hash=Hk3...
    """
    db = context.require_connected_db()
    assert isinstance(db, RCDBProvider)

    run = run_arg if run_arg is not None else run_opt

    if run is not None and file_hash is not None:
        raise click.UsageError("Provide either a run or --hash, not both.")
    if run is None and file_hash is None:
        raise click.UsageError("Provide a run (positional or --run) or --hash to select a file version.")

    if file_hash is not None:
        versions = db.session.query(ConfigurationFile) \
            .filter(ConfigurationFile.path == file_name) \
            .all()
        # Match by hash prefix in Python: the stored hash may be bytes or str
        # depending on the DB dialect, so we normalize before comparing.
        matches = [f for f in versions if _hash_str(f.sha256).startswith(file_hash)]
        if not matches:
            click.echo("No version of '{}' with hash '{}' found in DB.".format(file_name, file_hash), err=True)
            raise click.Abort()
        if len(matches) > 1:
            click.echo("Hash prefix '{}' is ambiguous, matches {} versions of '{}'."
                       .format(file_hash, len(matches), file_name), err=True)
            raise click.Abort()
        conf_file = matches[0]
    else:
        run_obj = db.get_run(run)
        if run_obj is None:
            click.echo("Run {} is not found in DB.".format(run), err=True)
            raise click.Abort()
        conf_file = db.get_file(run_obj, file_name)
        if conf_file is None:
            click.echo("No file '{}' attached to run {}.".format(file_name, run), err=True)
            raise click.Abort()

    # Raw dump so the output can be piped to e.g. grep
    click.echo(conf_file.content, nl=False)


# ---------------------------------------------------------------------------
# rcdb file runs <file name> [run filters] [--asc/--desc] [--limit]
# ---------------------------------------------------------------------------
@file_command.command(name="runs", help="List per-run versions of a file.")
@click.argument("file_name")
@click.option("--run-min", type=int, default=None, help="Lower run number bound (inclusive).")
@click.option("--run-max", type=int, default=None, help="Upper run number bound (inclusive).")
@click.option("--run", type=int, default=None, help="A single run number.")
@click.option("--run-period", default=None, help="A run period name.")
@click.option("--desc/--asc", "is_descending", default=True,
              help="Sort resulting runs descending (default) or ascending.")
@click.option("--limit", type=int, default=None, help="Limit the number of rows.")
@pass_rcdb_context
def file_runs(context, file_name, run_min, run_max, run, run_period, is_descending, limit):
    """List the runs that use FILE_NAME and the version (hash) used in each.

    Each row is printed as::

        <run number> - <file hash>

    Sorted by run number descending by default.
    """
    db = context.require_connected_db()
    assert isinstance(db, RCDBProvider)

    lo, hi = _resolve_run_range(db, run_min, run_max, run, run_period)

    order = desc if is_descending else asc
    query = db.session.query(Run.number, ConfigurationFile.sha256) \
        .join(ConfigurationFile.runs) \
        .filter(ConfigurationFile.path == file_name) \
        .filter(Run.number >= lo, Run.number <= hi) \
        .order_by(order(Run.number))

    if limit is not None:
        query = query.limit(limit)

    rows = query.all()
    if not rows:
        click.echo("No runs found for file '{}' in the given range.".format(file_name), err=True)
        return

    for run_number, sha256 in rows:
        click.echo("{} - {}".format(run_number, _hash_str(sha256)))


# ---------------------------------------------------------------------------
# rcdb file ls [run filters]
# ---------------------------------------------------------------------------
@file_command.command(name="ls", help="List all files for a run / run period.")
@click.argument("run_spec", required=False)
@click.option("--run-min", type=int, default=None, help="Lower run number bound (inclusive).")
@click.option("--run-max", type=int, default=None, help="Upper run number bound (inclusive).")
@click.option("--run", type=int, default=None, help="A single run number.")
@click.option("--run-period", default=None, help="A run period name.")
@pass_rcdb_context
def file_ls(context, run_spec, run_min, run_max, run, run_period):
    """List all files attached to runs in the given range, sorted by file name.

    Each row is printed as::

        <file hash> - <file name>

    The runs may be given either as a positional RUN_SPEC - a run number
    (``1000``), a run range (``1000-2000``) or a run period name - or with the
    --run/--run-min/--run-max/--run-period options. With no run filter, all
    files are listed.
    """
    db = context.require_connected_db()
    assert isinstance(db, RCDBProvider)

    if run_spec is not None:
        if any(x is not None for x in (run_min, run_max, run, run_period)):
            raise click.UsageError(
                "Provide either a positional run/range/period or the "
                "--run/--run-min/--run-max/--run-period options, not both.")
        lo, hi = _parse_run_spec(db, run_spec)
    else:
        lo, hi = _resolve_run_range(db, run_min, run_max, run, run_period)

    rows = db.session.query(ConfigurationFile.sha256, ConfigurationFile.path) \
        .join(ConfigurationFile.runs) \
        .filter(Run.number >= lo, Run.number <= hi) \
        .distinct() \
        .order_by(asc(ConfigurationFile.path)) \
        .all()

    if not rows:
        click.echo("No files found in the given range.", err=True)
        return

    for sha256, path in rows:
        click.echo("{} - {}".format(_hash_str(sha256), path))


# ---------------------------------------------------------------------------
# rcdb file search <pattern>
# ---------------------------------------------------------------------------
@file_command.command(name="search", help="Find file names containing a substring.")
@click.argument("pattern")
@pass_rcdb_context
def file_search(context, pattern):
    """Print all distinct file names whose path contains PATTERN as a substring.

    Matching is case-insensitive.
    """
    db = context.require_connected_db()
    assert isinstance(db, RCDBProvider)

    # Escape LIKE wildcards so '%' and '_' (common in file names) match literally.
    # ``ilike`` keeps the filter in the DB and is case-insensitive on all backends
    # (it compiles to ``lower(path) LIKE lower(?)`` on SQLite/MySQL).
    escaped = pattern.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

    rows = db.session.query(ConfigurationFile.path) \
        .filter(ConfigurationFile.path.ilike("%" + escaped + "%", escape="\\")) \
        .distinct() \
        .order_by(asc(ConfigurationFile.path)) \
        .all()

    for (path,) in rows:
        click.echo(path)

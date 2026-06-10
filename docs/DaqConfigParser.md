# DAQ Config Parser

The DAQ run configuration files produced by the Hall D CODA DAQ system are plain
text files split into named *sections* (TRIGGER, FCAL, BCAL, ...). RCDB ships a
small set of parsers that turn these files into Python objects.

## The config file format

A real config file looks like this:

```
#! Run type::  PHYSICS_8    Config::  TRG_FCAL_BCAL_m8_b1bf1.conf
#! CONFIG FILE:: /home/hdops/CDAQ/daq_dev_v0.31/daq/config/hd_all/TRG_FCAL_BCAL_m8_b1bf1.conf
#! (Re)Created:: on  Wed Apr 29 12:06:51 EDT 2015
#!

==========================
        TRIGGER
==========================

TS_TRIG_TYPE  6

# SSP      SLOT      FIBER_EN    SUM_ENABLE
SSP_SLOT     8         0xFF        1
...
```

Notes about the format:

- Lines that begin with `#` are comments. The header metadata lines use the
  `#!` marker, e.g. `#! (Re)Created::` (with the bang `!`).
- Lines made entirely of `====` or `----` are section separators and are ignored.
- A line whose first token equals one of the known section names (e.g. `TRIGGER`)
  starts a new section. Every subsequent line belongs to that section until the
  next section name.
- Inside a section, each line is split into tokens (using shell lexical rules,
  so quotes and `#` comments are honored). The first token is treated as a key.

## Parsers and import paths

There are three layers of parsers:

### 1. Generic parser — `rcdb.config_parser`

The low-level, section-name-agnostic parser. You pass the list of section names
you care about.

- `parse_file(filename, section_names)` -> `ConfigFileParseResult`
- `parse_content(content, section_names)` -> `ConfigFileParseResult`
- class `ConfigFileParseResult` with attributes:
  - `section_names` - the section names requested
  - `sections` - dict mapping section name -> `ConfigSection`
  - `found_section_names` - list of section names actually found in the file
- class `ConfigSection` with attributes:
  - `name` - the section name
  - `rows` - list of token lists (one per non-empty line in the section)
  - `entities` - dict of `key -> value`. For a 2-token line the value is a
    string; for a line with 3+ tokens the value is a list of the remaining tokens.

```python
from rcdb.config_parser import parse_file

result = parse_file("run-5627_FCAL_BCAL_PS_m7.conf", ["TRIGGER", "FCAL"])

print(result.found_section_names)               # ['TRIGGER', 'FCAL']
print(result.sections["TRIGGER"].entities["TS_TRIG_TYPE"])  # '6'
```

### 2. Hall D config parser — `halld_rcdb.run_config_parser`

The current Hall D parser. It calls the generic parser with the full Hall D
section list and then extracts known parameters (trigger equations/types, FADC
modes, per-subsystem COM/USER dir/version info, etc.).

- `parse_file(file_name)` -> `HallDMainConfigParseResult`
- `parse_content(content)` -> `HallDMainConfigParseResult`
- class `HallDMainConfigParseResult` wraps the raw `ConfigFileParseResult`
  (available as `.config_parse_result`) and exposes processed fields such as
  `trigger_type`, `trigger_eq`, `fcal_fadc250_files_info`,
  `ecal_fadc250_files_info`, `bcal_fadc250_files_info`, `cdc_fadc125_mode`,
  `ccal_fadc250_files_info`, `dirc_fadc250_files_info`, and more.

The supported section names are defined in `halld_rcdb/run_config_parser.py`:

```
TRIGGER, GLOBAL, FCAL, ECAL, BCAL, TOF, ST, TAGH, TAGM,
PS, PSC, TPOL, CDC, FDC, DIRC, CCAL
```

(ECAL, DIRC and CCAL are supported by this parser.)

### 3. Legacy parser — `rcdb.halld_daq_config_parser`

The original parser, kept for backwards compatibility. Prefer
`halld_rcdb.run_config_parser` for new code.

- `parse_file(filename)` -> `CodaRunLogParseResult`
- class `CodaRunLogParseResult` with `sections` (name -> `CodaRunLogSection`),
  `trigger_equation`, `trigger_type`, and a `section_names` property.
- class `CodaRunLogSection` with `name` and `lines`.

Its section list does **not** include ECAL, DIRC or CCAL:

```
TRIGGER, GLOBAL, FCAL, BCAL, TOF, ST, TAGH, TAGM, PS, PSC, TPOL, CDC, FDC
```

## Usage example

The `halld_rcdb` package lives next to the `rcdb` package in the `python/`
directory. Run the examples from there. Using `uv`:

```bash
cd python
uv --project ./python run python
```

```python
from halld_rcdb.run_config_parser import parse_file

result = parse_file("tests/run-5627_FCAL_BCAL_PS_m7.conf")

print(result.config_parse_result.found_section_names)
# ['TRIGGER', 'GLOBAL', 'FCAL', 'BCAL', 'TOF', 'ST', 'TAGH', 'TAGM', 'PS', 'PSC', 'TPOL', 'CDC', 'FDC']

print(result.trigger_type[0])
# ['PS', '440', '5', '1300', '1900', '1100', '0', '3']

print(result.fcal_fadc250_files_info)
# (com_dir, com_ver, user_dir, user_ver)
```

To run a one-off command without an interactive shell:

```bash
cd python
uv --project ./python run python -c "from halld_rcdb.run_config_parser import parse_file; \
print(parse_file('tests/run-5627_FCAL_BCAL_PS_m7.conf').config_parse_result.found_section_names)"
```

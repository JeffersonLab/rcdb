#!/bin/env python
#
# This script is used to load standard conditions information into the RCDB
# It sources the condition values from EPICS and the CCDB
#
# The following condition variables are currently loaded from this script:
#
# * beam_beam_energy       (float)  # Beam current - uses the primary epics BCM, IBCAD00CRCUR6
# * beam_energy            (float)  # Beam energy - from epics HALLD:p
# * coherent_peak          (float)  # Coherent peak location
# * collimator_diameter    (string) # Collimator diameter
# * luminosity             (float)  # Estimated luminosity factor
# * ps_converter           (string) # PS converter
# * solenoid_current       (float)  # Solenoid current
# * status                 (int)    # Run status - Rough information about run (e.g. is it "good" or not).
# * radiator_index         (int)    # Index of radiator position in goniometer
# * radiator_id            (int)    # ID of radiator in goniometer: unique id of diamond (0 for all amorphous)
# * polarization_direction (string) # Polarization direction - parallel or perpendicular to floor
# * radiator_type          (string) # Diamond name
# * target_type            (string) # Target type/status
#

# More description of these variables is provided below
#
# To call this script from other python code, use:
#     update_rcdb_conds(db, run_number)
#
# This script was originally written by Sean Dobbs (s-dobbs@northwestern.edu), 20 Apr. 2015
#      Updated: 28 Jan. 2016 (sdobbs)
#
import logging
import os,sys
import rcdb
from rcdb.model import ConditionType, Condition, Run
from epics import caget,caput
import subprocess
import datetime
from rcdb.log_format import BraceMessage as Lf

######################################

# Master function to update the conditions
def update_rcdb_conds(db, run):

    log = logging.getLogger('rcdb.update.epics')               # create run configuration standard logger
    log.debug(Lf("Running 'update_rcdb_conds(db={},   run={})'", db, run))

    TOLERANCE = 1.e-5  # constant used for comparisons
    # Run can be a rcdb.Run object or a run number
    if not isinstance(run, Run):
        log.debug(Lf("Getting run by number={}", run))
        run = db.get_run(run)

    # Build mapping of conditions to add to the RCDB, key is name of condition
    conditions = {}
    # Beam current - uses the primary BCM, IBCAD00CRCUR6
    # We could also use the following: IPM5C11.VAL,IPM5C11A.VAL,IPM5C11B.VAL,IPM5C11C.VAL
    try: 
        #conditions["beam_current"] = float(caget("IBCAD00CRCUR6"))   # pull the value at beam start?
        # save integrated beam current over the whole run
        # use MYA archive commands to calculate average

        # if the run has a set end time, then use that, otherwise use fallback
        if run.end_time:
            end_time = run.end_time
        else:
            time_delta = datetime.timedelta(minutes=10)
            now = datetime.datetime.now()
            end_time = now if now - run.start_time < time_delta else run.start_time + time_delta

            log.debug(Lf("No 'run.end_time'. Using '{}' as end_time", end_time))

        # Format begin and end time
        begin_time_str = datetime.datetime.strftime(run.start_time, '%Y-%m-%d %H:%M:%S')
        end_time_str = datetime.datetime.strftime(end_time, '%Y-%m-%d %H:%M:%S')
        log.debug(Lf("Requesting beam_current between  '{}' and '{}'", begin_time_str, end_time_str))

        # build myStats command
        cmds = ["myStats", "-b", begin_time_str, "-e", end_time_str, "-l", "IBCAD00CRCUR6"]
        log.debug(Lf("Requesting beam_current subprocess flags: '{}'", cmds))
        # execute external command
        p = subprocess.Popen(cmds, stdout=subprocess.PIPE)
        # iterate over output
        n = 0
        for line in p.stdout:
            n += 1
            if n == 1:     # skip header
                continue 
            tokens = line.strip().split()
            if len(tokens) < 3:
                continue
            key = tokens[0]
            value = tokens[2]      # average value
            if key == "IBCAD00CRCUR6":
                conditions["beam_current"] = float(value)

    except Exception as e:
        log.warn(Lf("Error in a beam_current request : '{}'", e))
        conditions["beam_current"] = -1.
    # Beam energy - HALLD:p gives the measured beam energy
    #             - MMSHLDE gives beam energy from model
    try: 
        # conditions["beam_energy"] = float(caget("HALLD:p"))
        # accelerator claims that measured beam energy isn't reliable 
        # below ~100 nA, so use model energy instead
        conditions["beam_energy"] = float(caget("MMSHLDE"))
    except:
        conditions["beam_energy"] = -1.
    # Solenoid current
    try: 
        conditions["solenoid_current"] = float(caget("HallD-PXI:Data:I_Shunt"))
    except:
        conditions["solenoid_current"] = -1.

    # ID of radiator in goniometer: unique id of diamond (0 for all amorphous)
    try:
        conditions["radiator_id"] = int(caget("HD:GONI:RADIATOR_ID"))
    except:
        conditions["radiator_id"] = -1.

    # Set a reasonable default for polarization direction - it should only be set
    # otherwise if we have a diamond radiator
    conditions["polarization_direction"] = "N/A"
        
    # only save information about the diamond radiator (or whatever is in the goniometer)
    # if the amorphous radiator is not in
    # yes, ID #5 is the retracted state
    # see:  https://halldsvn.jlab.org/repos/trunk/controls/epics/app/goniApp/Db/goni.substitutions
    if conditions["radiator_id"] != 5:
        # Polarization direction - parallel or perpendicular to floor
        try:
            polarization_dir = int(caget("HD:CBREM:PLANE"))
            if polarization_dir == 1:
                conditions["polarization_direction"] = "PARA"
            elif polarization_dir == 2:
                conditions["polarization_direction"] = "PERP"
        except:
            conditions["polarization_direction"] = "N/A"
            
        # Coherent peak location
        try:
            conditions["coherent_peak"] = float(caget("HD:CBREM:REQ_EDGE"))
        except:
            conditions["coherent_peak"] = -1.
        # Diamond name
        try:
            conditions["radiator_type"] = caget("HD:GONI:RADIATOR_NAME")
        except:
            conditions["radiator_type"] = ""
        # index of radiator position in goniometer
        try:
            conditions["radiator_index"] = caget("HD:GONI:RADIATOR_INDEX")
        except:
            conditions["radiator_index"] = -1.

    else:
        conditions["coherent_peak"] = -1.
        conditions["radiator_index"] = -1
        conditions["radiator_type"] = ""

    # Estimated luminosity factor - updated calculation in progress
    # conditions["luminosity"] = -1.
    # Run status - Used to store rough information about run (e.g. is it "good" or not).
    # Exact usage is still being discussed
    conditions["status"] = -1;
    # Collimator diameter
    try: 
        if abs(int(caget("hd:collimator_at_block"))) == 1:
            conditions["collimator_diameter"] = "Blocking"
        elif abs(int(caget("hd:collimator_at_a"))) == 1:
            conditions["collimator_diameter"] = "3.4mm hole"
        elif abs(int(caget("hd:collimator_at_b"))) == 1:
            conditions["collimator_diameter"] = "5.0mm hole"
        else:
            conditions["collimator_diameter"] = "Unknown"
    except:
        conditions["collimator_diameter"] = "Unknown"
    # Amorphous radiator
    if len(conditions["radiator_type"]) == 0:    # is non-zero only if amorphous, diamond name set earlier
        try: 
            if abs(int(caget("hd:radiator_at_a"))) == 1:
                conditions["radiator_type"] = "2x10-5 RL"
            elif abs(int(caget("hd:radiator_at_b"))) == 1:
                conditions["radiator_type"] = "1x10-4 RL"
            elif abs(int(caget("hd:radiator_at_c"))) == 1:
                conditions["radiator_type"] = "3x10-4 RL"
            else:
                conditions["radiator_type"] = "None"
        except:
            conditions["radiator_type"] = "Unknown"
    #  PS converter
    try: 
        if abs(int(caget("hd:converter_at_home"))) == 1:
            conditions["ps_converter"] = "Retracted"
        elif abs(int(caget("hd:converter_at_a"))) == 1:
            conditions["ps_converter"] = "1x10-3 RL"
        elif abs(int(caget("hd:converter_at_b"))) == 1:
            conditions["ps_converter"] = "3x10-4 RL"
        elif abs(int(caget("hd:converter_at_c"))) == 1:
            conditions["ps_converter"] = "5x10-3 RL"
        else:
            conditions["ps_converter"] = "Unknown"
    except:
        conditions["ps_converter"] = "Unknown"
    #  Polarimeter converter
    try: 
        if abs(int(caget("hd:polarimeter_at_home"))) == 1:
            conditions["polarimeter_converter"] = "Retracted"
        elif abs(int(caget("hd:polarimeter_at_a"))) == 1:
            conditions["polarimeter_converter"] = "Be 50um"
        elif abs(int(caget("hd:polarimeter_at_b"))) == 1:
            conditions["polarimeter_converter"] = "Be 75um"
        elif abs(int(caget("hd:polarimeter_at_c"))) == 1:
            conditions["polarimeter_converter"] = "Be 750um"
        else:
            conditions["polarimeter_converter"] = "Unknown"
    except:
        conditions["polarimeter_converter"] = "Unknown"
    # hydrogen target status
    # caget HLD:TGT:status.ZRST   // OFF
    # caget HLD:TGT:status.ONST   // Cooling
    # caget HLD:TGT:status.TWST   // Filling
    # caget HLD:TGT:status.THST   // FULL & Ready
    # caget HLD:TGT:status.FRST   // Emptying
    # caget HLD:TGT:status.FVST   // EMPTY & Ready
    try: 
        conditions["target_type"] = caget("HLD:TGT:status", as_string=True)
    except:
        conditions["target_type"] = "Unknown"

    # Add all the values that we've determined to the RCDB
    for (key, value) in conditions.items():
        log.debug(Lf("Adding cnd '{}'='{}'", key, value))

    db.add_conditions(run, conditions, True)

    log.debug("Committed to DB. End of update_rcdb_conds()")
    return conditions

# entry point
if __name__ == "__main__":
    log = logging.getLogger('rcdb.update')               # create run configuration standard logger
    log.addHandler(logging.StreamHandler(sys.stdout))    # add console output for logger
    log.setLevel(logging.DEBUG)                          # print everything. Change to logging.INFO for less output

    #db = rcdb.RCDBProvider("sqlite:///"+sys.argv[1])
    #db = rcdb.RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb")
    #db = rcdb.RCDBProvider("mysql://rcdb@gluondb1/rcdb")
    update_rcdb_conds(db, int(sys.argv[1]))

    #query = db.session.query(Run).filter(Run.number > 9999)
    #print query.all() 
    #for run in query.all():
    #    update_rcdb_conds(db, run.number)

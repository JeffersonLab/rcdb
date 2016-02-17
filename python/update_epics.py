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
import os,sys
import rcdb
from rcdb.model import ConditionType, Condition, Run
from epics import caget,caput
import subprocess
import datetime

######################################

# Master function to update the conditions
def update_rcdb_conds(db, run):
    TOLERANCE = 1.e-5  # constant used for comparisons

    # Build mapping of conditions to add to the RCDB, key is name of condition
    conditions = {}
    # Beam current - uses the primary BCM, IBCAD00CRCUR6
    # We could also use the following: IPM5C11.VAL,IPM5C11A.VAL,IPM5C11B.VAL,IPM5C11C.VAL
    try: 
        #conditions["beam_current"] = float(caget("IBCAD00CRCUR6"))   # pull the value at beam start?
        # save integrated beam current over the whole run
        # use MYA archive commands to calculate average

        # get the start time for the run
        rundata = db.get_run(run)    
        begintime = datetime.datetime.strftime(rundata.start_time, '%Y-%m-%d %H:%M:%S')
        # if the run has a set end time, then use that, otherwise use the current time
        if rundata.end_time:
            endtime = datetime.datetime.strftime(rundata.end_time, '%Y-%m-%d %H:%M:%S')
        else:
            endtime = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')  # current date/time

        # build myStats command
        cmds = []
        cmds.append("myStats")
        cmds.append("-b")
        cmds.append(begintime)
        cmds.append("-e")
        cmds.append(endtime)
        cmds.append("-l")
        cmds.append("IBCAD00CRCUR6")
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
            value = tokens[2]    ## average value
            if key == "IBCAD00CRCUR6":
                conditions["beam_current"] = float(value)
    except:
        conditions["beam_current"] = -1.
    #except Exception,e:
    #    print str(e)
    # Beam energy - HALLD:p gives the measured beam energy
    #             - MMSHLDE gives beam energy from model
    try: 
        #conditions["beam_energy"] = float(caget("HALLD:p"))
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
            else:
                conditions["polarization_direction"] = "UNKNOWN"
        except:
            conditions["polarization_direction"] = "UNKNOWN"
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
        conditions["polarization_direction"] = "N/A"
        conditions["radiator_index"] = -1
        conditions["radiator_type"] = ""

    # Estimated luminosity factor - updated calculation in progress
    # conditions["luminosity"] = -1.
    # Run status - Used to store rough information about run (e.g. is it "good" or not).
    # Exact usage is still being discussed
    conditions["status"] = -1;
    # Collimator diameter
    try: 
        if abs(float(caget("hd:collimator_at_block")) - 1.) < TOLERANCE:
            conditions["collimator_diameter"] = "Blocking"
        elif abs(float(caget("hd:collimator_at_a")) - 1.) < TOLERANCE:
            conditions["collimator_diameter"] = "3.4mm hole"
        elif abs(float(caget("hd:collimator_at_b")) - 1.) < TOLERANCE:
            conditions["collimator_diameter"] = "5.0mm hole"
    except:
        conditions["collimator_diameter"] = "Unknown"
    # Amorphous radiator
    if len(conditions["radiator_type"]) == 0:    # is non-zero only if amorphous, diamond name set earlier
        try: 
            if abs(float(caget("hd:radiator_at_a")) - 1.) < TOLERANCE:
                conditions["radiator_type"] = "2x10-5 RL"
            elif abs(float(caget("hd:radiator_at_b")) - 1.) < TOLERANCE:
                conditions["radiator_type"] = "1x10-4 RL"
            elif abs(float(caget("hd:radiator_at_c")) - 1.) < TOLERANCE:
                conditions["radiator_type"] = "3x10-4 RL"
            else:
                conditions["radiator_type"] = "None"
        except:
            conditions["radiator_type"] = "Unknown"
    #  PS converter
    try: 
        if abs(float(caget("hd:converter_at_home")) - 1.) < TOLERANCE:
            conditions["ps_converter"] = "Retracted"
        elif abs(float(caget("hd:converter_at_a")) - 1.) < TOLERANCE:
            conditions["ps_converter"] = "1x10-3 RL"
        elif abs(float(caget("hd:converter_at_b")) - 1.) < TOLERANCE:
            conditions["ps_converter"] = "3x10-4 RL"
        elif abs(float(caget("hd:converter_at_c")) - 1.) < TOLERANCE:
            conditions["ps_converter"] = "5x10-3 RL"
    except:
        conditions["ps_converter"] = "Unknown"
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
    for (key,value) in conditions.items():
        db.add_condition(run, key, value, None, True, auto_commit=False)
    db.session.commit()

# entry point
if __name__ == "__main__":
    #db = rcdb.RCDBProvider("sqlite:///"+sys.argv[1])
    #db = rcdb.RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb")
    #db = rcdb.RCDBProvider("mysql://rcdb@gluondb1/rcdb")
    update_rcdb_conds(db, int(sys.argv[1]))

    #query = db.session.query(Run).filter(Run.number > 9999)
    #print query.all() 
    #for run in query.all():
    #    update_rcdb_conds(db, run.number)

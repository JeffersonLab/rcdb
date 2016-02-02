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
#

# More description of these variables is provided below
#
# To call this script from other python code, use:
#     update_rcdb_condspolarization_direction.update_rcdb_conds(db, run_number)
#
# This script was originally written by Sean Dobbs (s-dobbs@northwestern.edu), 20 Apr. 2015
#      Updated: 28 Jan. 2016 (sdobbs)
#
import os,sys
import rcdb
from epics import caget,caput

######################################

# Master function to update the conditions
def update_rcdb_conds(db, run):
    TOLERANCE = 1.e-5  # constant used for comparisons

    # Build mapping of conditions to add to the RCDB, key is name of condition
    conditions = {}
    # Beam current - uses the primary BCM, IBCAD00CRCUR6
    # We could also use the following: IPM5C11.VAL,IPM5C11A.VAL,IPM5C11B.VAL,IPM5C11C.VAL
    try: 
        conditions["beam_current"] = float(caget("IBCAD00CRCUR6"))
    except:
        conditions["beam_current"] = -1.
    # Beam energy - HALLD:p gives the measured beam energy
    try: 
        conditions["beam_energy"] = float(caget("HALLD:p"))
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
    if conditions["radiator_id"] != 0:
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
    #conditions["luminosity"] = -1.
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
    

    # Add all the values that we've determined to the RCDB
    for (key,value) in conditions.items():
        db.add_condition(run, key, value, None, True)

# entry point
if __name__ == "__main__":
    db = rcdb.RCDBProvider("sqlite:///"+sys.argv[1])
    update_rcdb_conds(db, int(sys.argv[2]))

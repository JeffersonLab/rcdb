#!/bin/env python
#
# This script is used to load standard conditions information into the RCDB
# It sources the condition values from EPICS and the CCDB
#
# This script can be used standalone as:
#   > python3 update_epics.py <db_password> <run_num> <reason>
# where <reason> is one of start, update, end
#
# The following condition variables are currently loaded from this script:
#
# * beam_beam_energy       (float)  # Beam current - uses the primary epics BCM, IBCAD00CRCUR6
# * beam_energy            (float)  # Beam energy - from epics HALLD:p
# * cdc_gas_pressure       (float)  # Gas pressure related to CDC.  EPICS: RESET:i:GasPanelBarPress1
# * coherent_peak          (float)  # Coherent peak location
# * collimator_diameter    (string) # Collimator diameter
# * halfwave_plate         (string) # Is the insertable half wave plate in or not?
# * luminosity             (float)  # Estimated luminosity factor
# * ps_converter           (string) # PS converter
# * solenoid_current       (float)  # Solenoid current
# * status                 (int)    # Run status - Rough information about run (e.g. is it "good" or not).
# * radiator_index         (int)    # Index of radiator position in goniometer
# * radiator_id            (int)    # ID of radiator in goniometer: unique id of diamond (0 for all amorphous)
# * polarization_direction (string) # Polarization direction - parallel or perpendicular to floor
# * radiator_type          (string) # Diamond name
# * target_type            (string) # Target type/status
# * tagger_current         (float)  # Current in tagger magnet
# * wien_angle_horizontal  (float)  # Various Wien Angle measurements 
# * wien_angle_solenoid    (float)
# * wien_angle_vertical    (float)
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


# Logging

log = logging.getLogger('rcdb.update.epics')               # create run configuration standard logger
######################################

def update_beam_conditions(run, log):
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


    try: 
        # also, get the current excluding periods when the beam is off
        # we define this as the periods where the BCM reads 5 - 5000 nA
        cmds = ["myStats", "-b", begin_time_str, "-e", end_time_str, "-c", "IBCAD00CRCUR6", "-r", "5:5000", "-l", "IBCAD00CRCUR6"]
        log.debug(Lf("Requesting beam_current subprocess flags: '{}'", cmds))
        # execute external command
        p = subprocess.Popen(cmds, stdout=subprocess.PIPE)
        # iterate over output
        n = 0
        for line in p.stdout:
            print(line.strip())
            n += 1
            if n == 1:     # skip header
                continue 
            tokens = line.strip().split()
            if len(tokens) < 3:
                continue
            key = tokens[0]
            value = tokens[2]      # average value
            if key == "IBCAD00CRCUR6":
                conditions["beam_on_current"] = float(value)
        log.debug("Done with beam_current")
    except Exception as e:
        log.warn(Lf("Error in a beam_current request : '{}'", e))
        conditions["beam_on_current"] = -1.


    try: 
        # also get the beam energy when current > 35 nA and beam energy > 10. MeV, to avoid problems
        # where the CEBAF beam energy server fails and doesn't restart =(

        avg_beam_energy = 0.
        nentries = 0
        cmds = ["myData", "-b", begin_time_str, "-e", end_time_str, "IBCAD00CRCUR6", "HALLD:p"]
        log.debug(Lf("Requesting beam_energy subprocess flags: '{}'", cmds))
        # execute external command
        p = subprocess.Popen(cmds, stdout=subprocess.PIPE)

        # wait process end and iterate over output
        n = 0
        for line in p.stdout:
            print(line.strip())
            n += 1
            if n == 1:     # skip header
                continue 
            tokens = line.strip().split()
            if len(tokens) < 4:
                continue
            the_beam_current = float(tokens[2])
            the_beam_energy = float(tokens[3])
            if (the_beam_current>35.) and (the_beam_energy>10.):
                avg_beam_energy += the_beam_energy
                nentries += 1
        log.debug("Done with beam_energy")
        # experience has shown that the above myData command returns once or twice every second...
        # so let's ignore the time periods and do a simple average
        #avg_beam_energy /= float(n)
        conditions["beam_energy"] = float("%7.1f"%(avg_beam_energy / float(nentries)))

        """
        cmds = ["myStats", "-b", begin_time_str, "-e", end_time_str, "-c", "IBCAD00CRCUR6", "-r", "30:5000", "-l", "HALLD:p"]
        log.debug(Lf("Requesting beam_energy subprocess flags: '{}'", cmds))
        # execute external command
        p = subprocess.Popen(cmds, stdout=subprocess.PIPE)
        # iterate over output
        n = 0
        for line in p.stdout:
            print(line.strip())
            n += 1
            if n == 1:     # skip header
                continue 
            tokens = line.strip().split()
            if len(tokens) < 3:
                continue
            key = tokens[0]
            value = tokens[2]      # average value
            if key == "HALLD:p":
                conditions["beam_energy"] = float(value)
        """

    except Exception as e:
        log.warn(Lf("Error in a beam_energy request : '{}'", e))
        conditions["beam_energy"] = -1.


    try: 
        # also, get the average CDC gas pressure
        cmds = ["myStats", "-b", begin_time_str, "-e", end_time_str, "-l", "RESET:i:GasPanelBarPress1"]
        log.debug(Lf("Requesting cdc_gas_pressure subprocess flags: '{}'", cmds))
        # execute external command
        p = subprocess.Popen(cmds, stdout=subprocess.PIPE)
        # iterate over output
        n = 0
        for line in p.stdout:
            print(line.strip())
            n += 1
            if n == 1:     # skip header
                continue 
            tokens = line.strip().split()
            if len(tokens) < 3:
                continue
            key = tokens[0]
            value = tokens[2]      # average value
            if key == "RESET:i:GasPanelBarPress1":
                conditions["cdc_gas_pressure"] = float(value)
        log.debug("Done with cdc_gas_pressure")
    except Exception as e:
        log.warn(Lf("Error in a cdc_gas_pressure request : '{}'", e))
        conditions["cdc_gas_pressure"] = -1.

    return conditions


# noinspection PyBroadException
def setup_run_conds(run):
    # Build mapping of conditions to add to the RCDB, key is name of condition
    conditions = {}
    log.debug("Start of setup_run_conds()")

    # Beam energy - HALLD:p gives the measured beam energy
    #             - MMSHLDE gives beam energy from model
    try: 
        conditions["beam_energy"] = float(caget("HALLD:p"))
        # conditions["beam_energy"] = float(caget("MMSHLDE"))
    except:
        conditions["beam_energy"] = -1.
    # Beam current from the tagger dump BCM
    try: 
        conditions["beam_current"] = float(caget("IBCAD00CRCUR6"))
    except:
        conditions["beam_current"] = -1.
    # CDC gas pressure
    try: 
        conditions["cdc_gas_pressure"] = float(caget("RESET:i:GasPanelBarPress1"))
    except:
        conditions["cdc_gas_pressure"] = -1.
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

    # set global radiator name
    try:
        conditions["radiator_type"] = caget("hd:radiator:uname")  # this always fails!
    except:
        conditions["radiator_type"] = None
        
    # only save information about the diamond radiator (or whatever is in the goniometer)
    # if the amorphous radiator ladder is not in
    # yes, ID #1 is the retracted state, ID #2 is the blank state... for 2016 at least.
    # 12/7/2017: #5000 is the retracted state, and all of the non-diamond radiators have ID #0.
    # the diamonds have more complicated IDs
    # see:  https://halldsvn.jlab.org/repos/trunk/controls/epics/app/goniApp/Db/goni.substitutions
    if conditions["radiator_id"] != 5000:
        # Save diamond info only if we aren't using an amorphous radiator
        if conditions["radiator_id"] != 0:
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
        else:
            conditions["coherent_peak"] = -1.
            conditions["polarization_direction"] = "N/A"

        # radiator name
        if conditions["radiator_type"] is None:
            try:
                conditions["radiator_type"] = caget("HD:GONI:RADIATOR_NAME")
            except:
                conditions["radiator_type"] = ""
        # index of radiator position in goniometer
        try:
            conditions["radiator_index"] = caget("HD:GONI:RADIATOR_INDEX")
        except:
            conditions["radiator_index"] = -1.
        # fix polarization_direction for amorphous radiator in goniometer
        if conditions["radiator_type"].find("Al") >= 0:
            conditions["polarization_direction"] = "N/A"
    else:
        conditions["coherent_peak"] = -1.
        conditions["radiator_index"] = -1
        conditions["radiator_type"] = ""
        conditions["polarization_direction"] = "N/A"


    # set polarization angle
    conditions["polarization_angle"] = None
    if conditions["radiator_type"].find("0/90") >= 0:
        if conditions["polarization_direction"] == "PARA":
            conditions["polarization_angle"] = 0.
        elif conditions["polarization_direction"] == "PERP":
            conditions["polarization_angle"] = 90.
    elif conditions["radiator_type"].find("45/135") >= 0:
        if conditions["polarization_direction"] == "PARA":
            conditions["polarization_angle"] = 135.
        elif conditions["polarization_direction"] == "PERP":
            conditions["polarization_angle"] = 45.

    if conditions["polarization_angle"] == None:
        conditions["polarization_angle"] = -1.

    # Estimated luminosity factor - updated calculation in progress
    # conditions["luminosity"] = -1.
    # Run status - Used to store rough information about run (e.g. is it "good" or not).
    # Exact usage is still being discussed
    conditions["status"] = -1
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
    if conditions["radiator_type"] is None:
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

    # Insertable Half-wave plate
    try: 
        conditions["halfwave_plate"] = caget("IGL1I00DI24_24M", as_string=True)
    except:
        conditions["halfwave_plate"] = "Unknown"

    # Various Wien Angle measurements                                                                                                                                                                                                           
    try: 
        conditions["wien_angle_horizontal"] = float(caget("PWF1I06:spinCalc"))
    except:
        conditions["wien_angle_horizontal"] = -1.
    try: 
        conditions["wien_angle_solenoid"] = float(caget("MFGANGLE"))
    except:
        conditions["wien_angle_solenoid"] = -1.
    try: 
        conditions["wien_angle_vertical"] = float(caget("PWF1I04:spinCalc"))
    except:
        conditions["wien_angle_vertical"] = -1.

    log.debug(Lf("End of setup_run_conds. Conditions gathered: '{}'", conditions.keys()))
    return conditions


# Master function to update the conditions
def update_rcdb_conds(db, run, reason):
    log.debug(Lf("Running 'update_rcdb_conds(db={},   run={})'", db, run))

    TOLERANCE = 1.e-5  # constant used for comparisons
    # Run can be a rcdb.Run object or a run number
    if not isinstance(run, Run):
        log.debug(Lf("Getting run by number={}", run))
        run = db.get_run(run)

    # Build mapping of conditions to add to the RCDB, key is name of condition
    conditions = {}

    if reason == "start":
        conditions.update(setup_run_conds(run))

    if reason in ["update", "end"]:
        conditions.update(update_beam_conditions(run, log))
        
    # Debug output with the list of conditions
    log.debug(Lf("Name value of updating conditions:"))
    for (key, value) in conditions.items():
        log.debug(Lf("   '{}' = '{}'", key, value))

    # Add all the values that we've determined to the RCDB
    db.add_conditions(run, conditions, True)

    log.debug("Committed to DB. End of update_rcdb_conds()")
    return conditions

# entry point
if __name__ == "__main__":
    log.addHandler(logging.StreamHandler(sys.stdout))    # add console output for logger
    log.setLevel(logging.DEBUG)                          # print everything. Change to logging.INFO for less output

    if len(sys.argv) < 4:
        print("""
This script usage
 > python3 update_epics.py <db_password> <run_num> <reason>
where <reason> is one of: start, update, end""")
        exit(1)

    # Main program shell take
    # db = rcdb.RCDBProvider("sqlite:///"+sys.argv[1])
    # db = rcdb.RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb")
    password = sys.argv[1]
    run_number = int(sys.argv[2])
    update_reason = sys.argv[3]

    db = rcdb.RCDBProvider("mysql://rcdb:%s@gluondb1/rcdb"%password)
    if not db.get_run(run_number):
        raise ValueError("Run number '{}' is not found in DB", run_number)
    update_rcdb_conds(db, run_number, update_reason)

    #query = db.session.query(Run).filter(Run.number > 9999)
    #print(query.all())
    #for run in query.all():
    #    update_rcdb_conds(db, run.number)

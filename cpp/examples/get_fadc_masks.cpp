/**
 *
 * (!) strong advice: see 'get_trigger_params.cpp' example first (!)
 *
 * This example follows get_trigger_params example. After getting main config section,
 * we open FCAL FADC configuration file and read masks from it
 *
 *  This document illustrates:
 *  a. How to get FADC masks
 *
 *  The values from trigger section (and how they are defined there):
 *
 *      BLOCKLEVEL 1                # so it is name-value
 *
 *      TS_TRIG_HOLD  10  1         # that is name-array
 *
 *      TRIG_TYPE  PS     440 ...   # array lines that occurs met many times
 *      TRIG_TYPE  BFCAL  440 ...
 *      ...
 *
 *      TRIG_EQ  PS      35   ...   # Same as TRIG_TYPE - array which occurs many times
 *      TRIG_EQ  BCAL_E  20   ...
 *
 *  To do this, in terma of RCDB C++ API we have to perform the following steps:
 *
 *  1. Connect to DB
 *  2. Read 'rvts' condition, that holds run config file name (we need the name for the next step)
 *  3. Get run config file from the DB
 *  4. Parse file contents (that will five us ConfigFileParseResult)
 *  5. Get required data out of ConfigFileParseResult
 *
 */

#include <string>
#include <vector>

#include <iostream>



#include "RCDB/Connection.h"
#include "RCDB/ConfigParser.h"


using namespace std;

vector<string> MainConfigSectionNames = {"TRIGGER", "GLOBAL", "FCAL", "BCAL", "TOF", "ST", "TAGH",
                                     "TAGM", "PS", "PSC", "TPOL", "CDC", "FDC"};



rcdb::ConfigFileParseResult GetMainConfigParsed(rcdb::Connection &connection, int runNumber)
{
    // ==> 2. Get rtvs condition, that contains config file name for the given run
    auto rtvsCondition = connection.GetCondition(runNumber, "rtvs");    // Get condition by run and name
    if(!rtvsCondition) {
        cout<<"'rtvs' condition is not set for run "<<runNumber<<endl;
        throw std::logic_error("'rtvs' condition is not set for run ");
    }


    auto json = rtvsCondition->ToJsonDocument();                        // The CODA rtvs is serialized as JSon dictionary.

    string fileName(json["%(config)"].GetString());                     // We need item with name '%(config)'
    // That is our file name


    // ==> 3. Get file out of RCDB (by run number and name)
    auto file = connection.GetFile(runNumber, fileName);
    if(!file) {                                                         // If there is no such file, null is returned
        cout<<"File with name: "<< fileName
            <<" doesn't exist (not associated) with run: "<< runNumber << endl;
        throw std::logic_error("File doesn't exist for (or is not associated with) run");
    }


    // ==> 4. Parse run config file content
    string fileContent = file->GetContent();                                // Get file content
    return rcdb::ConfigParser::Parse(fileContent, MainConfigSectionNames);  // Parse it and return
}

/**
  * Lets say for run 30229
  * (open in by this link https://halldweb.jlab.org/rcdb/runs/info/30229 )
  * Main config file has section FCAL
  * which has fields that say, what config files where used for FADC250:
  *   FADC250_COM_DIR      /gluex/CALIB/ALL/fadc250/default
  *   FADC250_COM_VER      default
  *   FADC250_USER_DIR     /gluonfs1/gluex/CALIB/FCAL/fadc250/user/spring_2016
  *   FADC250_USER_VER     ring2_hot_v2
  *
  * for 'rocfcal8' we have configuration file which has:
  *   #################
  *   FADC250_SLOTS  3
  *   #################
  *
  *   #       channel:   0   1   2   3   4   5   6   7   8   9   10   11   12   13   14   15
  *   FADC250_TRG_MASK   0   0   0   0   1   1   1   1   1   1    1    1    1    1    0    0
  *
  * We want values of FADC250_TRG_MASK done right
  * (read from user config or from common config if there is no user config)
  */

int main ( int argc, char *argv[] )
{
 using namespace std;

 // ==> 0. PREPARE
 if ( argc != 3 ) {
     cout<<"This example gets some trigger parameters for a specified run"<<endl;
     cout<<"usage: "<< argv[0] <<" <connection_string> <run_number>"<<endl;
     cout<<"exmpl: "<< argv[0] <<" mysql://rcdb@hallddb.jlab.org/rcdb 30229"<<endl;

     return 1;
 }
 string connection_str(argv[1]);         // Get a connection string from arguments
 int runNumber = atoi(argv[2]);             // The run number, we work with

 // ==> 1. Create DB connection
 rcdb::Connection connection(connection_str);

// PARSE main config file
    auto mainCfgParseResult = GetMainConfigParsed(connection, runNumber);
    auto runFileNames = connection.GetFileNames(runNumber);


    // GET COM_DIR USER_DIR values
    string comDir  = mainCfgParseResult.Sections["FCAL"].NameValues["FADC250_COM_DIR"];
    string comVer  = mainCfgParseResult.Sections["FCAL"].NameValues["FADC250_COM_VER"];
    string userDir = mainCfgParseResult.Sections["FCAL"].NameValues["FADC250_USER_DIR"];
    string userVer = mainCfgParseResult.Sections["FCAL"].NameValues["FADC250_USER_VER"];

    string comFileName = comDir + "/rocfcal8_fadc250_" + comVer + ".cnf";
    string userFileName = userDir + "/rocfcal8_" + userVer + ".cnf";

    // PRINT EVERYTHING
    cout<<"FADC250_COM_DIR   "<<comDir <<endl;
    cout<<"FADC250_COM_VER   "<<comVer <<endl;
    cout<<"FADC250_USER_DIR  "<<userDir<<endl;
    cout<<"FADC250_USER_VER  "<<userVer<<endl;

    cout<<"Result COM and USER file names:"<<endl;
    cout<<"    "<<comFileName<<endl;
    cout<<"    "<<userFileName<<endl;


    // get all file names for this run
    cout<<"All files saved for run "<<runNumber<<endl;
    for (int i = 0; i < runFileNames.size(); ++i) {
        cout<<"    "<<runFileNames[i]<<endl;
    }


    // Get COM file out of database
    auto comFile = connection.GetFile(runNumber, comFileName);
    if(!comFile) {                                                         // If there is no such file, null is returned
        cout<<"COM File with name: "<< comFileName<<" doesn't exist (not associated) with run: "<< runNumber << endl;
        throw std::logic_error("COM File doesn't exist for (or is not associated with) run");
    }

    // Parse COM file and get values from com FILE
    auto comParseResult = rcdb::ConfigParser::ParseWithSlots(comFile->GetContent(), "FADC250_SLOTS");
    auto comValues = comParseResult.SectionsBySlotNumber[3].NameVectors["FADC250_ALLCH_THR"];  // Parse it and return

    cout<<"FADC250_ALLCH_THR for slot 3 is:"<<endl;
    for (int i = 0; i < comValues.size(); ++i) {
        cout<<"    "<<comValues[i]<<endl;
    }

    // Now get USER file out of database
    auto userFile = connection.GetFile(runNumber, userFileName);
    if(!userFile) {                                                         // If there is no such file, null is returned

        cout<<"USER File with name: "<< userFileName
            <<" doesn't exist (not associated) with run: "<< runNumber << "returning COM file results"<<endl;
        return 1;

    }
    // Parse COM file and get values from com FILE
    auto userParseResult = rcdb::ConfigParser::ParseWithSlots(userFile->GetContent(), "FADC250_SLOTS");
    auto userValues = comParseResult.SectionsBySlotNumber[3].NameVectors["FADC250_TRG_MASK"];  // Parse it and return

    cout<<"FADC250_TRG_MASK for slot 3 is:"<<endl;
    for (int i = 0; i < userValues.size(); ++i) {
        cout<<"    "<<userValues[i]<<endl;
    }
 // Lets say we want to get values for roc8
 // First we check it is
 return 0;
}

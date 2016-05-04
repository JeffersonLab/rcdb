/** This example shows how to get several values from TRIGGER section of the run configuration file.
 *
 *  This document illustrates:
 *  a. How to parse config file and get values from config parser
 *  b. How to get config file from the database
 *  c. How to get config file name from CODA 'rtvs'
 *  d. How to deal with maps and arrays saved as JSon
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

vector<string> SectionNames = {"TRIGGER", "GLOBAL", "FCAL", "BCAL", "TOF", "ST", "TAGH",
                                         "TAGM", "PS", "PSC", "TPOL", "CDC", "FDC"};



int main ( int argc, char *argv[] )
{
    using namespace std;

    // ==> 0. PREPARE
    if ( argc != 3 ) {
        cout<<"This example gets some trigger parameters for a specified run"<<endl;
        cout<<"usage: "<< argv[0] <<" <connection_string> <run_number>"<<endl;
        cout<<"exmpl: "<< argv[0] <<" mysql://rcdb@hallddb.jlab.org/rcdb 10200"<<endl;

        return 1;
    }
    string connection_str(argv[1]);         // Get a connection string from arguments
    int runNumber = atoi(argv[2]);             // The run number, we work with



    // ==> 1. Create DB connection
    rcdb::Connection connection(connection_str);



    // ==> 2. Get rtvs condition, that contains config file name for the given run
    auto rtvsCondition = connection.GetCondition(runNumber, "rtvs");    // Get condition by run and name
    if(!rtvsCondition) {
        cout<<"'rtvs' condition is not set for run "<<runNumber<<endl;
        return 2;
    }


    auto json = rtvsCondition->ToJsonDocument();                        // The CODA rtvs is serialized as JSon dictionary.

    string fileName(json["%(config)"].GetString());                     // We need item with name '%(config)'
                                                                        // That is our file name


    // ==> 3. Get file out of RCDB (by run number and name)
    auto file = connection.GetFile(runNumber, fileName);
    if(!file) {                                                         // If there is no such file, null is returned
        cout<<"File with name: "<< fileName
            <<" doesn't exist (not associated) with run: "<< runNumber << endl;
        return 3;
    }


    // ==> 4. Parse run config file content
    string fileContent = file->GetContent();                               // Get file content
    auto result = rcdb::ConfigParser::Parse(fileContent, SectionNames);    // Parse it!

    // NameValues member of Sections contains things like 'BLOCKLEVEL 1'
    cout<<"BLOCKLEVEL = "<<result.Sections["TRIGGER"].NameValues["BLOCKLEVEL"]<< endl;

    // NameVectors contains all lines with name-multiple values, like 'TS_TRIG_HOLD  10  1'
    vector<string> trig_holds =  result.Sections["TRIGGER"].NameVectors["TS_TRIG_HOLD"];
    cout<<"TS_TRIG_HOLD = ";
    for (auto val: trig_holds){
        cout<<val<<", ";
    }
    cout<<endl;

    // All lines of section go to Rows. To get TRIG_TYPE and TRIG_EQ we grep through lines:
    vector<vector<string>> triggerTypes;
    vector<vector<string>> triggerEqs;

    // Get all TRIG_TYPE from TRIGGER section
    for(auto row : result.Sections["TRIGGER"].Rows) {
        if(row[0] == "TRIG_TYPE") {
            triggerTypes.push_back(row);    // The line starts with TRIG_TYPE
        }
        if(row[0] == "TRIG_EQ") {
            triggerEqs.push_back(row);      // The line starts with TRIG_EQ
        }
    }

    // Print the results
    cout<<"TRIG_TYPEs:"<<endl;
    for(auto line: triggerTypes) {
        for(auto cell: line) cout<<cell<<" ";
        cout<<endl<<endl;
    }

    cout<<"TRIG_TYPEs:"<<endl;
    for(auto line: triggerTypes) {
        for(auto cell: line) cout<<cell<<" ";
        cout<<endl<<endl;
    }

    return 0;
}

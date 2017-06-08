/**
 *  This example shows how to work with json stored objects
 *  RCDB uses json library
 *  https://github.com/nlohmann/json
 */
#include <string>
#include <iostream>

#include "RCDB/WritingConnection.h"
#include "json/json.hpp"

using json = nlohmann::json;

int main(int argc, char *argv[]) {
    using namespace std;
    using namespace rapidjson;

    // Get a connection string from arguments
    if (argc != 2) {
        cout << "This example writes objects as json for a specified run" << endl;
        cout<<"rcnd --create json_cnd --type json --description \"JSON serialized values\""<<endl;
        cout << "usage: " << argv[0] << " <connection_string>" << endl;
        cout << "exmpl: " << argv[0] << " mysql://rcdb@localhost/rcdb" << endl;
        cout << "exmpl: " << argv[0] << " mysql://rcdb:password@clondb1/rcdb" << endl;
        return 1;
    }
    string connection_str(argv[1]);

    // Create DB connection
    rcdb::WritingConnection connection(connection_str);

    struct tm start_time;

    start_time.tm_year = 2016 - 1900;
    start_time.tm_mon = 1;
    start_time.tm_mday = 4;
    start_time.tm_hour = 02;
    start_time.tm_min = 30;
    start_time.tm_sec = 38;
    start_time.tm_isdst = 0;

    struct tm end_time;

    end_time.tm_year = 2016 - 1900;
    end_time.tm_mon = 1;
    end_time.tm_mday = 4;
    end_time.tm_hour = 04;
    end_time.tm_min = 25;
    end_time.tm_sec = 10;
    end_time.tm_isdst = 0;

    connection.AddRun(999);
    connection.AddRunStartTime(999, start_time);
    connection.AddRunEndTime(999, end_time);


/*
id      name    value_type      created         description
1       event_count     int     2017-03-15 14:18:55     Number of events in run
2       events_rate     float   2017-03-15 14:18:55     Daq events rate
3       temperature     int     2017-03-15 14:18:55     Temperature of the Sun
4       beam_energy     float   2017-03-15 18:57:22     Beam Energy
5       test    float   2017-03-15 18:58:00     Beam test
6       beam_current    float   2017-03-15 19:02:10     Beam current
7       torus_scale     float   2017-03-15 19:02:10     Torus scale factor
8       daq_trigger     string  2017-03-15 19:02:10     Trigger file
9       target_position         float   2017-03-15 19:02:10     Target position
10      daq_comment     string  2017-03-15 19:02:10     DAQ comment
11      run_start_time  time    2017-04-21 10:28:49     Run start time
12      run_end_time    time    2017-04-21 10:29:02     Run end time
13      is_valid_run_end        bool    2017-04-21 10:48:35     True if a run has valid run-end record. False mean...
14      status  int     2017-05-17 13:30:34     Run Status
*/

    int32_t event_count = 12345;
    float events_rate = 98765.32;
    int32_t temperature = 77;
    float beam_energy = 6.095;
    float test = 1234567890.123;
    string daq_trigger = "trigger_file_name";
    string daq_comment = "this run is junk";
    std::vector<int> c_vector{1, 2, 3, 4};


    // P A R T   1 - w r i t i n g   a r r a y

    // You can create json a way, which looks very similar to the JSON itself)
    json j = {
            {"event_count", event_count},
            {"events_rate", events_rate},
            {"temperature", temperature},
            {"beam_energy", beam_energy},
            {"daq_trigger", daq_trigger},
            {"test",        test},
            {"list",        {1, 0, true}},
            {"object",      {{"currency", "USD"}, {"value", 42.99}}},
            {"c_vector", c_vector},
            {"start_time", StringUtils::GetFormattedTime(start_time)}
        };


    // or act as a dictionary
    // add a number that is stored as double (note the implicit conversion of j to an object)
    j["pi"] = 3.141;

    // Pretty formatted json
    cout<<j.dump(4)<<endl;

    // compact formatted json
    cout<<j.dump()<<endl;

    // Add condition
    connection.AddCondition(999, "json_cnd", j.dump());


    // P A R T   2 - r e a d i n g   a r r a y

    auto cnd = connection.GetCondition(999, "json_cnd");
    auto data = cnd->ToJson();

    // iterate as the array
    for (json::iterator it = data.begin(); it != data.end(); ++it) {
        std::cout << *it << '\n';
    }

    // range-based for
    for (auto& element : data) {
        std::cout << element << '\n';
    }


    int32_t ev_cnt = data["event_count"];

    // explicit data conversion
    auto trigger = data["daq_trigger"].get<std::string>();

    cout<<"trigger= "<<trigger<<"   start_time="<<data["start_time"]<<endl;

    return 0;
}
/**
 *  This is very simple example of how to save an array to JSON.
 *  RCDB bundles the taocpp/json library:
 *  https://github.com/taocpp/json
 */
#include <string>
#include <iostream>

#include "RCDB/WritingConnection.h"

#include <tao/json.hpp>


int main ( int argc, char *argv[] )
{
    using namespace std;
    using namespace tao;

    // Get a connection string from arguments
    if ( argc != 2 ) {
        cout<<"This example writes some array as json field for a specified run"<<endl;
        cout<<"Before run, create condition types as follows:"<<endl;
        cout<<"rcnd --create json_cnd --type json --description \"JSON serialized values\""<<endl;
        cout<<"usage: "<< argv[0] <<" <connection_string>"<<endl;
        cout<<"exmpl: "<< argv[0] <<" mysql://rcdb@localhost/rcdb"<<endl;
        return 1;
    }
    string connection_str(argv[1]);

    // Create DB connection
    rcdb::WritingConnection connection(connection_str);

    struct tm start_time;

    start_time.tm_year = 2016-1900;
    start_time.tm_mon = 1;
    start_time.tm_mday = 4;
    start_time.tm_hour = 02;
    start_time.tm_min = 30;
    start_time.tm_sec = 38;
    start_time.tm_isdst = 0;

    struct tm end_time;

    end_time.tm_year = 2016-1900;
    end_time.tm_mon = 1;
    end_time.tm_mday = 4;
    end_time.tm_hour = 04;
    end_time.tm_min = 25;
    end_time.tm_sec = 10;
    end_time.tm_isdst = 0;


    connection.AddRun(999);
    connection.AddRunStartTime(999, start_time);
    connection.AddRunEndTime(999, end_time);

    // P A R T   1 - w r i t i n g   a r r a y

    //We want to store some value and array to JSON file
    auto document = json::value::array({});             // a JSON value holding an (empty) array
    for(int i=-5; i<5; i++)
    {
        document.emplace_back(i);                       // Put array values
    }

    // Convert document to string
    string output = tao::json::to_string(document);

    // Print the JSon we've got
    cout<<"Resulting json is:"<<endl;
    cout<<output<<endl;

    // Add json condition
    connection.AddCondition(999, "json_cnd", output);

    // P A R T   2 - r e a d i n g   a r r a y
    auto cnd = connection.GetCondition(999, "json_cnd");
    auto json = tao::json::from_string(cnd->ToString());

    // since we saved json as array, we can iterate it directly
    for(const auto& item : json.get_array())
    {
        std::cout<<" "<< item.get_signed();
    }
    std::cout<<endl;


    // That is our file name
    return 0;
}
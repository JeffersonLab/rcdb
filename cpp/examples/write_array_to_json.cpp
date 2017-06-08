/**
 *  This is very simple example of how to save array to JSON using rapidjson
 *  Full RapidJson documentation is available here:
 *  http://rapidjson.org/index.html
 */
#include <string>
#include <iostream>

#include "RCDB/WritingConnection.h"


#include "rapidjson/stringbuffer.h"
#include "rapidjson/writer.h"


int main ( int argc, char *argv[] )
{
    using namespace std;
    using namespace rapidjson;

    // Get a connection string from arguments
    if ( argc != 2 ) {
        cout<<"This example gets event_count for a specified run"<<endl;
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


    connection.AddRun(998);
    connection.AddRunStartTime(999, start_time);
    connection.AddRunEndTime(999, end_time);

    // P A R T   1 - w r i t i n g   a r r a y

    //We want to store some value and array to JSON file
    Document document;
    document.SetArray();                                // document must be SetArray or SetObject
    auto& allocator = document.GetAllocator();          // You... just need this allocator. Imagine this is mantra
    for(int i=-5; i<5; i++)
    {
        document.PushBack(Value().SetInt(i), allocator);  // Put array values
    }

    // Convert document to string
    StringBuffer buffer;
    Writer<StringBuffer> writer(buffer);
    document.Accept(writer);
    string output = buffer.GetString();

    // Print the JSon we've got
    cout<<"Resulting json is:"<<endl;
    cout<<output<<endl;

    // Add json condition
    connection.AddCondition(999, "json_cnd", output);

    // P A R T   2 - r e a d i n g   a r r a y
    auto cnd = connection.GetCondition(999, "json_cnd");
    auto json = cnd->ToJsonDocument();

    //string fileName(json["%(config)"].GetString());                     // We need item with name '%(config)'

    // since we saved json as array, we can iterate it directly
    for(int i=0; i<json.Size(); i++)
    {
        std::cout<< json[i].GetInt();
    }
    std::cout<<endl;


    // That is our file name
    return 0;
}
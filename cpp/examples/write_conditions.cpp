/**
 *
 */
#include <string>
#include <iostream>


#include "RCDB/WritingConnection.h"

int main ( int argc, char *argv[] )
{
    using namespace std;

    // Get a connection string from arguments
    if ( argc != 2 ) {
        cout<<"This example gets event_count for a specified run"<<endl;
        cout<<"Before run, create condition types as follows:"<<endl;
        cout<<"rcnd --create int_cnd --type int --description \"Int value\""<<endl;
        cout<<"rcnd --create float_cnd --type float --description \"Float value\""<<endl;
        cout<<"rcnd --create time_cnd --type time --description \"Time value\""<<endl;
        cout<<"rcnd --create text_cnd --type string --description \"Text value\""<<endl;
        cout<<"rcnd --create bool_cnd --type bool --description \"Bool value\""<<endl;
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

    connection.AddCondition(999, "int_cnd", (long)5);
    connection.AddCondition(999, "float_cnd", 13.2);
    connection.AddCondition(999, "time_cnd", end_time);
    connection.AddCondition(999, "text_cnd", "haha! it works!");
    connection.AddCondition(999, "bool_cnd", true);



    // Get condition by run and name
    // Set:
    // run = 10452, 'event_count' if you connect to a real database
    // run = 1, 'int_cnd' if you connect to a test database
    //auto cnd = connection.GetCondition(1, "int_cnd");
    auto cnd = connection.GetCondition(999, "int_cnd");

    //cnd will be null if no such condition saved for the run
    if(!cnd)
    {
        cout<<"The condition is not found for the run"<<endl;
        return 2;
    }

    // get the value!
    int value = cnd->ToInt();
    cout<<"event_count is: "<< value << endl;
    return 0;
}


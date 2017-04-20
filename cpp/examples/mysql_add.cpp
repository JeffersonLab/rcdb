//
// Adds constant to
//

#include <string>
#include <iostream>

#include "RCDB/Connection.h"


int main ( int argc, char *argv[] )
{
    using namespace std;

    // Get a connection string from arguments
    if ( argc != 3 ) {
        cout<<"This example gets event_count for a specified run"<<endl;
        cout<<"usage: "<< argv[0] <<" <connection_string> <value>"<<endl;
        cout<<"exmpl: "<< argv[0] <<" mysql://rcdb@localhost/rcdb 10452"<<endl;
        return 1;
    }
    string connection_str(argv[1]);
    int run = atoi(argv[2]);

    // Create DB connection
    rcdb::Connection connection(connection_str);

    // Get condition by run and name
    // Set:
    // run = 10452, 'event_count' if you connect to a real database
    // run = 1, 'int_cnd' if you connect to a test database
    //auto cnd = connection.GetCondition(1, "int_cnd");
    auto cnd = connection.GetCondition(run, "event_count");

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
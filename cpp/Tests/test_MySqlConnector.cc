#pragma warning(disable:4800)
#include "Tests/catch.hpp"
#include <vector>

#include "TDB/MySqlConnector.h"
#include "TDB/Error.h"

using namespace std;
//using namespace ccdb;

bool test_DMySQLDataProviderConnection();  //Test basic connection

/********************************************************************* ** 
 * @brief Test basic connection
 *
 * @return true if test passed
 */
TEST_CASE("TDB/MySqlConnector/Usual behaviour","Connection tests")
{
    tdb::MySqlConnector conn;

    //Check that we have a right setup after construction"
    {
        REQUIRE_FALSE(conn.IsConnected());
    }

    //Try to connecto to database"
    {
        auto error = conn.Connect("127.0.0.1", "triggerdb", "", "triggerdb", 0, NULL, 0);    
        REQUIRE_FALSE(error);
        REQUIRE(conn.IsConnected());
    }

    //Try to disconnect and reconnect
    {        
        auto error = conn.Disconnect();

        REQUIRE_FALSE(error);
        REQUIRE_FALSE(conn.IsConnected());

        error = conn.Connect("127.0.0.1", "triggerdb", "", "triggerdb", 0, NULL, 0);    
        REQUIRE_FALSE(error);
        REQUIRE(conn.IsConnected());
    }
    
    //Try to get data from connector
    {
        vector<vector<string> > table; 

        auto error = conn.QuerySelect(table, "SELECT * from boards");
        REQUIRE_FALSE(error);
        REQUIRE(table.size()>=2);
        REQUIRE(table[0].size()>=7);
    }
}


TEST_CASE("TDB/MySqlConnector/StressTests","Connection tests")
{

    SECTION("NoConnection query", "Try to query not connected object")    
    {  
        tdb::MySqlConnector conn;
        vector<vector<string> > table; 
        auto error = conn.QuerySelect(table, "SELECT * from boards");
        REQUIRE(error);
    }
}
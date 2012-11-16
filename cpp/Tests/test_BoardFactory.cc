#pragma warning(disable:4800)
#include "Tests/catch.hpp"
#include <vector>


#include "TDB/BoardFactory.h"
#include "TDB/Error.h"
#include "TDB/Board.h"

using namespace std;
//using namespace ccdb;

bool test_DMySQLDataProviderConnection();  //Test basic connection

/********************************************************************* ** 
 * @brief Test basic connection
 *
 * @return true if test passed
 */
TEST_CASE("TDB/BoardFactory","Test of boards database loader")
{
    shared_ptr<tdb::MySqlConnector> conn(new tdb::MySqlConnector());
    REQUIRE_FALSE(conn->Connect("127.0.0.1", "triggerdb", "", "triggerdb", 0, NULL, 0));
    tdb::BoardFactory bf(conn);

    SECTION("Construction", "Check that we have a right setup after construction")
    {
        
    }

    
    SECTION("Get all boards", "Get all boards from database")
    {
        tdb::board_vector boards;
        auto result = bf.LoadBoards(boards);
        REQUIRE_FALSE(result);

    }
    



}

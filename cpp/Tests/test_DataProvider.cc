#pragma warning(disable:4800)
#include "Tests/catch.hpp"
#include <vector>

#include "TDB/Board.h"
#include "TDB/BoardFactory.h"
#include "TDB/DataProvider.h"
#include "TDB/Error.h"

using namespace std;
using namespace tdb;

bool test_DMySQLDataProviderConnection();  //Test basic connection

/********************************************************************* ** 
 * @brief Test basic connection
 *
 * @return true if test passed
 */
TEST_CASE("TDB/DataProvider","Test data provider")
{
    DataProvider prov;
    REQUIRE_FALSE(prov.Database()->Connect("127.0.0.1", "triggerdb", "", "triggerdb", 0, NULL, 0));
    board_vector boards;
    REQUIRE_FALSE(prov.Boards()->LoadBoards(boards));
    REQUIRE(boards.size()>=2);
}

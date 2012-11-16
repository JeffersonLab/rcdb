#pragma warning(disable:4800)
#include "Tests/catch.hpp"
#include <vector>

#include "TDB/Board.h"
#include "TDB/Error.h"

using namespace std;
//using namespace ccdb;

bool test_DMySQLDataProviderConnection();  //Test basic connection

/********************************************************************* ** 
 * @brief Test basic connection
 *
 * @return true if test passed
 */
TEST_CASE("TDB/Board","Board class tests")
{
    tdb::Board board;

    SECTION("Construction", "Check that we have a right setup after construction")
    {
        
    }   
}

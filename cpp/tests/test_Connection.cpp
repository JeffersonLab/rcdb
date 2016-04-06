#include "catch.hpp"
#include "RCDB/Connection.h"
#include <cstdlib>


using namespace rcdb;
using namespace std;

TEST_CASE("General test of Connection", "[connection]") {

    const char* env_p = std::getenv("RCDB_TEST_CONNECTION");
    if(!env_p) {
        FAIL("Environment variable RCDB_TEST_CONNECTION is not set");
    }


    Connection prov(env_p);

    auto cnd = prov.GetCondition(1, string("int_cnd"));
    REQUIRE(cnd);
    REQUIRE(cnd->ToInt() == 5);


    cnd = prov.GetCondition(99999999999, string("int_cnd"));
    REQUIRE_FALSE(cnd);
}


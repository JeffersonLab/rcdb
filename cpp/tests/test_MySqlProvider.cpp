//
// Created by romanov on 1/23/16.
//
#include "catch.hpp"
#include "RCDB/MySqlProvider.h"
#include <cstdlib>


using namespace rcdb;
using namespace std;

TEST_CASE("General test of MySql", "[mysql]") {

    const char* env_p = std::getenv("RCDB_TEST_CONNECTION");
    if(!env_p) {
        FAIL("Environment variable RCDB_TEST_CONNECTION is not set");
    }


    if(string(env_p).find("mysql://") == string::npos) {
        // The test only works with MySQL
        return;
    }



    MySqlProvider prov(env_p);

    auto cnd = prov.GetCondition(1, string("int_cnd"));
    REQUIRE(cnd);
    REQUIRE(cnd->ToInt() == 5);


    cnd = prov.GetCondition(99999999999, string("int_cnd"));
    REQUIRE_FALSE(cnd);


}

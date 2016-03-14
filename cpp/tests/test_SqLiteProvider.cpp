//
// Created by romanov on 1/23/16.
//
#include "catch.hpp"
#include "RCDB/SqLiteProvider.h"

using namespace rcdb;


TEST_CASE("General test of SqLite", "[sqlite]") {
    using namespace std;
    string path("/home/romanov/gluex/rcdb/rcdb/rcdb/python/tests/test.sqlite.db");
    SqLiteProvider prov(path);
    prov.SetRun(1);
    auto cnd = prov.GetCondition(string("int_cnd"));
    REQUIRE(cnd);
    REQUIRE(cnd->ToInt() == 5);

    prov.SetRun(99999999999);
    cnd = prov.GetCondition(string("int_cnd"));
    REQUIRE_FALSE(cnd);


}
//
// Created by romanov on 1/23/16.
//


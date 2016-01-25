//
// Created by romanov on 1/23/16.
//
#include "catch.hpp"
#include "RCDB/MySqlProvider.h"

using namespace rcdb;


TEST_CASE("General test of MySql", "[mysql]") {
    MySqlProvider prov;
    prov.Test();
}

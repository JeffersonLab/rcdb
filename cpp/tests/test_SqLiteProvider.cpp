//
// Created by romanov on 1/23/16.
//
#include "catch.hpp"
#include "RCDB/SqLiteProvider.h"

using namespace rcdb;


TEST_CASE("General test of SqLite", "[sqlite]") {
    SqLiteProvider prov;
    prov.Test();
}
//
// Created by romanov on 1/23/16.
//


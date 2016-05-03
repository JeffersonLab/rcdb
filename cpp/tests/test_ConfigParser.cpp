//
// Created by romanov on 4/29/16.
//

#include <string>
#include <vector>

#include "catch.hpp"
#include "RCDB/ConfigParser.h"

static std::string TestConfig(R"(
#  F1TDC_WINDOW    1000.0  <- Trigger window (ns)

==========================
TRIGGER
==========================

#CALIBRATION   1


TS_TRIG_TYPE  6
TS_TRIG_TYPE  7

TS_FP_INPUTS  3   9  10  12

#            TYPE       DELAY     INT_WIDTH     ENABLE

TRIG_EQ      PS          35         10           1
TRIG_EQ      BCAL_E      15         20           1

==========================
GLOBAL
==========================

F1TDC_BIN_SIZE   0.058

)");



using namespace rcdb;
using namespace std;

TEST_CASE("Test of config parser", "[config_parser]") {

    vector<string> sections = {"TRIGGER", "GLOBAL", "NON_EXISTENT"};

    auto result = ConfigParser::Parse(TestConfig, sections);

    REQUIRE(result.Sections.size() == 2);
    REQUIRE(result.Sections["TRIGGER"].Rows.size() == 5);
    REQUIRE(result.Sections["TRIGGER"].NameValues["TS_TRIG_TYPE"] == "7");
}



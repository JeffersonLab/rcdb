#include "catch.hpp"
#include "RCDB/SqLiteProvider.h"

#include <chrono>
#include <ctime>
#include <string>

using namespace rcdb;

TEST_CASE("General test of SqLite", "[sqlite]")
{
    using namespace std;

    const char* env = std::getenv("RCDB_TEST_CONNECTION");
    if(env == nullptr) {
        FAIL("Environment variable RCDB_TEST_CONNECTION is not set");
    }


    if(string(env).find("sqlite://") == string::npos) {
        INFO("Connection string is not SQLite exiting SQLite provider tests");
        CAPTURE(env)
        // The test only works with SQLite
        return;
    }

    string path(env);
    SqLiteProvider prov(path);

    auto cnd = prov.GetCondition(1, string("int_cnd"));
    REQUIRE(cnd);
    REQUIRE(cnd->ToInt() == 5);


    cnd = prov.GetCondition(99999999999, string("int_cnd"));
    REQUIRE_FALSE(cnd);

    // Regression test for issue #90: ToTime() used to read int_value (NULL for a
    // time condition) instead of the time_value string, returning the Unix epoch
    // (1970-01-01). It must return the stored time. Fixture: time_cnd for run 1
    // is 2016-03-11 00:59:09 (interpreted as UTC).
    auto timeCnd = prov.GetCondition(1, string("time_cnd"));
    REQUIRE(timeCnd);
    std::time_t t = std::chrono::system_clock::to_time_t(timeCnd->ToTime());
    REQUIRE(t != 0);                                       // not the epoch
    char buf[32];
    std::strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", std::gmtime(&t));
    REQUIRE(string(buf) == "2016-03-11 00:59:09");
    // ToString() now also returns the raw stored datetime for Time conditions.
    REQUIRE(timeCnd->ToString().substr(0, 19) == "2016-03-11 00:59:09");
}


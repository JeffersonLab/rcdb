// Equivalence tests for Condition::ToJsonDocument().
//
// ToJsonDocument() used to return a rapidjson::Document; it now returns a
// tao::json::value parsed from the condition's text. These tests pin that the
// new implementation produces the SAME parsed JSON (keys, types, numbers,
// nested arrays/objects) the old rapidjson version did -- exercised on a real
// CODA 'rtvs' dictionary and on a rich payload covering every JSON node type.
//
// A one-off A/B against a local rapidjson build confirmed byte/structure
// equivalence (rapidjson parse+serialize, re-parsed by tao, equals tao's direct
// parse for all payloads below). rapidjson is no longer in the tree, so this
// committed test relies only on tao.

#include "catch.hpp"
#include "RCDB/Condition.h"
#include <tao/json.hpp>
#include <cstdint>

using namespace rcdb;

namespace {
    // Build a Json-typed Condition holding the given serialized JSON text.
    Condition makeJsonCondition(ConditionType& type, const std::string& text) {
        type.SetValueType(ValueTypes::Json);
        Condition cnd(type);
        cnd.SetTextValue(text);
        return cnd;
    }
}

TEST_CASE("ToJsonDocument parses a real CODA rtvs dictionary", "[condition][json]") {
    // A representative slice of a production 'rtvs' condition (string -> string).
    const std::string rtvs =
        "{\"%(CODA_ROL2)\":\"/home/hdops/CDAQ/daq_dev_v0.31/daq/vme/src/rol_2\","
        "\"%(udl)\":\"cMsg://gluon102.jlab.org:45000/cMsg/hdops/?regime=low\","
        "\"%(config)\":\"/home/hdops/CDAQ/daq_dev_v0.31/daq/config/hd_bcal_n/led_upstream_mode8.cnf\","
        "\"%(rn)\":\"2471\","
        "\"%(DAQ_HOME)\":\"/home/hdops/CDAQ/daq_dev_v0.31/daq\"}";

    ConditionType type;
    Condition cnd = makeJsonCondition(type, rtvs);
    auto json = cnd.ToJsonDocument();

    // The exact accessor the trigger-sim / get_trigger_params use.
    REQUIRE(json.at("%(config)").get_string() ==
            "/home/hdops/CDAQ/daq_dev_v0.31/daq/config/hd_bcal_n/led_upstream_mode8.cnf");
    REQUIRE(json.at("%(rn)").get_string() == "2471");
    REQUIRE(json.is_object());
    REQUIRE(json.get_object().size() == 5);

    // Strong equivalence: value-equal (order-independent) to an independently
    // constructed expected document.
    const tao::json::value expected = tao::json::value({
        {"%(CODA_ROL2)", "/home/hdops/CDAQ/daq_dev_v0.31/daq/vme/src/rol_2"},
        {"%(udl)",       "cMsg://gluon102.jlab.org:45000/cMsg/hdops/?regime=low"},
        {"%(config)",    "/home/hdops/CDAQ/daq_dev_v0.31/daq/config/hd_bcal_n/led_upstream_mode8.cnf"},
        {"%(rn)",        "2471"},
        {"%(DAQ_HOME)",  "/home/hdops/CDAQ/daq_dev_v0.31/daq"},
    });
    REQUIRE(json == expected);
}

TEST_CASE("ToJsonDocument preserves every JSON node type", "[condition][json]") {
    const std::string rich =
        "{\"str\":\"hello\",\"int\":42,\"neg\":-7,\"float\":3.5,\"big\":1234567890,"
        "\"bool\":true,\"nul\":null,\"arr\":[1,2,3],\"mixed\":[\"a\",2,false],"
        "\"nested\":{\"a\":[true,false],\"b\":\"x\",\"c\":{\"d\":9}}}";

    ConditionType type;
    Condition cnd = makeJsonCondition(type, rich);
    auto json = cnd.ToJsonDocument();

    // Numbers: tao stores unsigned positive ints as 'unsigned' and negatives as
    // 'signed', so use the coercing as<T>() accessor rather than get_signed().
    // (Value equality across number storage is what the rapidjson A/B confirmed.)
    REQUIRE(json.at("str").get_string() == "hello");
    REQUIRE(json.at("int").as<std::int64_t>() == 42);
    REQUIRE(json.at("neg").as<std::int64_t>() == -7);
    REQUIRE(json.at("float").as<double>() == Approx(3.5));
    REQUIRE(json.at("big").as<std::int64_t>() == 1234567890);
    REQUIRE(json.at("bool").get_boolean() == true);
    REQUIRE(json.at("nul").is_null());

    const auto& arr = json.at("arr").get_array();
    REQUIRE(arr.size() == 3);
    REQUIRE(arr[0].as<std::int64_t>() == 1);
    REQUIRE(arr[2].as<std::int64_t>() == 3);

    const auto& mixed = json.at("mixed").get_array();
    REQUIRE(mixed[0].get_string() == "a");
    REQUIRE(mixed[1].as<std::int64_t>() == 2);
    REQUIRE(mixed[2].get_boolean() == false);

    // nested object + array
    REQUIRE(json.at("nested").at("b").get_string() == "x");
    REQUIRE(json.at("nested").at("c").at("d").as<std::int64_t>() == 9);
    REQUIRE(json.at("nested").at("a").get_array().at(0).get_boolean() == true);

    // Round-trip fidelity: parsing via ToJsonDocument yields exactly what a plain
    // tao parse of the same text yields (no mangling of structure/values).
    REQUIRE(json == tao::json::from_string(rich));
}

namespace {
    // Returns true iff ToJsonDocument() throws rcdb::ValueFormatError. Catches by
    // const reference (REQUIRE_THROWS_AS catches by value -> -Wcatch-value).
    bool throwsValueFormatError(Condition& cnd) {
        try {
            cnd.ToJsonDocument();
        } catch (const rcdb::ValueFormatError&) {
            return true;
        }
        return false;
    }
}

TEST_CASE("ToJsonDocument enforces the same error contract as before", "[condition][json]") {
    SECTION("non-Json value type throws ValueFormatError") {
        ConditionType type;
        type.SetValueType(ValueTypes::String);
        Condition cnd(type);
        cnd.SetTextValue("{\"a\":1}");
        REQUIRE(throwsValueFormatError(cnd));
    }
    SECTION("malformed JSON throws ValueFormatError") {
        ConditionType type;
        Condition cnd = makeJsonCondition(type, "{not valid json");
        REQUIRE(throwsValueFormatError(cnd));
    }
}

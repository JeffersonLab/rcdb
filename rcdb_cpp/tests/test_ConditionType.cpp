#include "catch.hpp"
#include "RCDB/ConditionType.h"

using namespace rcdb;


TEST_CASE("Value types to string correspondence", "[model]") {
    REQUIRE(std::string("bool") == ConditionType::ValueTypeToString(ValueTypes::Bool));
    REQUIRE(std::string("json") == ConditionType::ValueTypeToString(ValueTypes::Json));
    REQUIRE(std::string("string") == ConditionType::ValueTypeToString(ValueTypes::String));
    REQUIRE(std::string("float") == ConditionType::ValueTypeToString(ValueTypes::Float));
    REQUIRE(std::string("int") == ConditionType::ValueTypeToString(ValueTypes::Int));
    REQUIRE(std::string("time") == ConditionType::ValueTypeToString(ValueTypes::Time));
    REQUIRE(std::string("blob") == ConditionType::ValueTypeToString(ValueTypes::Blob));


    REQUIRE(ConditionType::StringToValueType("int") == ValueTypes::Int);
    REQUIRE(ConditionType::StringToValueType("float") == ValueTypes::Float);
    REQUIRE(ConditionType::StringToValueType("string") == ValueTypes::String);
    REQUIRE(ConditionType::StringToValueType("bool") == ValueTypes::Bool);
    REQUIRE(ConditionType::StringToValueType("json") == ValueTypes::Json);
    REQUIRE(ConditionType::StringToValueType("time") == ValueTypes::Time);
    REQUIRE(ConditionType::StringToValueType("blob") == ValueTypes::Blob);
}

TEST_CASE("One more test", "[model]") {

}

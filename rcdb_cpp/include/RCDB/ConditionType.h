//
// Created by romanov on 1/23/16.
//

#ifndef RCDB_CPP_CONDITIONTYPE_H
#define RCDB_CPP_CONDITIONTYPE_H

#include <stddef.h>
#include <cstdint>
#include <string>
#include <exception>
#include <stdexcept>

namespace rcdb {

    enum class ValueTypes {
        Bool,
        Json,
        String,
        Float,
        Int,
        Time,
        Blob
    };


    class ConditionType {
    public:
        static std::string ValueTypeToString(ValueTypes type) {
            switch (type) {
                case ValueTypes::Bool :
                    return std::string("bool");
                case ValueTypes::Json :
                    return std::string("json");
                case ValueTypes::String :
                    return std::string("string");
                case ValueTypes::Float :
                    return std::string("float");
                case ValueTypes::Int :
                    return std::string("int");
                case ValueTypes::Time :
                    return std::string("time");
                case ValueTypes::Blob :
                    return std::string("blob");
                default:
                    throw std::logic_error("ValueTypes type is something different than one of possible values");
            }
        }

        static ValueTypes StringToValueType(std::string str) {
            if (std::string("int") == str) return ValueTypes::Int;
            else if (std::string("float") == str) return ValueTypes::Float;
            else if (std::string("string") == str) return ValueTypes::String;
            else if (std::string("bool") == str) return ValueTypes::Bool;
            else if (std::string("json") == str) return ValueTypes::Json;
            else if (std::string("time") == str) return ValueTypes::Time;
            else if (std::string("blob") == str) return ValueTypes::Blob;
            throw std::logic_error(
                    "ValueTypes string '" + str + "' is something different than one of possible values");
        }

        uint64_t GetId() const { return _id; }
        void SetId(uint64_t id) { _id = id; }

        const std::string &GetName() const { return _name; }
        void SetName(const std::string &name) { _name = name; }

        const ValueTypes &GetValueType() const { return _valueType; }
        void SetValueType(const ValueTypes &valueType) { _valueType = valueType; }

        uint64_t _id = 0;
        std::string _name;
        ValueTypes _valueType = ValueTypes::Float;
    };
}


#endif //RCDB_CPP_CONDITIONTYPE_H

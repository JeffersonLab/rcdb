//
// Created by romanov on 1/28/16.
//

#ifndef RCDB_CPP_CONDITION_H
#define RCDB_CPP_CONDITION_H

#include "ConditionType.h"
#include "Exceptions.h"
#include <chrono>
#include <string>
#include <tao/json.hpp>   // ToJsonDocument() returns a tao::json::value (was rapidjson)

class DataProvder;

namespace rcdb {

    class Condition {
    public:
        Condition(ConditionType &conditionType) :
                _type(conditionType) {

        }

        /** Returns value of the condition as int.
         * Throws if ValueType is not int in DB
         * */
        int ToInt() {

            if (GetValueType() != ValueTypes::Int) {
                throw rcdb::ValueFormatError("Value type of the condition is not int");
            }
            return _int_value;
        }


        /** Returns value of the condition as Bool.
         * If ValueType is int it is converted to bool
         *
         * Throws if ValueType is not bool or int in DB
         */
        bool ToBool() {

            if (GetValueType() != ValueTypes::Int && GetValueType() != ValueTypes::Bool) {
                throw rcdb::ValueFormatError("Value type of the condition is not bool or int");
            }
            if (GetValueType() == ValueTypes::Int) return _int_value;

            return _bool_value;
        }

        /** Returns value of the condition as Double.
         * If ValueType is int it is converted to Double
         *
         * Throws if ValueType is not Double or int in DB
         */
        double ToDouble() {

            if (GetValueType() != ValueTypes::Int && GetValueType() != ValueTypes::Float) {
                throw rcdb::ValueFormatError("Value type of the condition is not 'Float'(double in C++) or int");
            }

            if (GetValueType() == ValueTypes::Int) return _int_value;

            return _float_value;
        }

        /** Returns value of the condition as string.
         * Works for ValueTypes Json, String, Blob
         *
         * Throws if ValueType is not Json, String or Blob in DB
         */
        std::string ToString() {

            if (GetValueType() != ValueTypes::Json &&
                GetValueType() != ValueTypes::String &&
                GetValueType() != ValueTypes::Blob &&
                GetValueType() != ValueTypes::Time) {
                throw rcdb::ValueFormatError("Value type of the condition is not String, Json, Blob or Time");
            }

            // For Time values this is the raw stored datetime string
            // ("YYYY-MM-DD HH:MM:SS"); use ToTime() for a parsed time_point.
            return _text_value;
        }


        /** Returns the condition value parsed as a JSON document.
         *
         *  Only valid when the condition's value type is Json (e.g. the CODA 'rtvs'
         *  dictionary). This is a drop-in for the historical rapidjson implementation:
         *  the same text is parsed into the same JSON structure/values -- only the
         *  returned type changed from rapidjson::Document to tao::json::value, so the
         *  header no longer depends on rapidjson. Callers keep `auto json = ...;` but
         *  use tao's accessors (e.g. json.at("%(config)").get_string()) instead of
         *  rapidjson's (json["%(config)"].GetString()).
         *
         *  Throws rcdb::ValueFormatError if the value type is not Json, or the text is
         *  not parseable JSON -- the same error contract as the old implementation.
         */
        tao::json::value ToJsonDocument()
        {
            if (GetValueType() != ValueTypes::Json) {
                throw rcdb::ValueFormatError("Value type of the condition is not Json");
            }

            try {
                return tao::json::from_string(_text_value);
            } catch (const std::exception &) {
                throw rcdb::ValueFormatError("Error while parsing JSon");
            }
        }


        /** Returns value of the condition as time_point.
         *
         * Throws if ValueType is not Time in DB
         */
        std::chrono::time_point<std::chrono::system_clock>
        ToTime() {

            if (GetValueType() != ValueTypes::Time) {
                throw rcdb::ValueFormatError("Value type of the condition is not Time");
            }

            return _time;
        }

        /**
         * Returns the type @see(rcdb::ValueTypes) of the value of this condition
         */
        rcdb::ValueTypes GetValueType() { return _type.GetValueType(); }


        void SetId(unsigned long id) {
            _id = id;
        }

        unsigned long GetId() {
            return _id;
        }

        void SetRunNumber(unsigned long runNumber) {
            _runNumber = runNumber;
        }

        void SetTextValue(const std::string &text_value) {
            _text_value = text_value;
        }

        void SetIntValue(int int_value) {
            _int_value = int_value;
        }

        void SetFloatValue(double float_value) {
            _float_value = float_value;
        }

        void SetBoolValue(bool bool_value) {
            _bool_value = bool_value;
        }

        void SetTime(std::chrono::time_point<std::chrono::system_clock> time) {
            _time = time;
        }

    private:
        unsigned long _id;
        unsigned long _runNumber;
        std::string _text_value;
        int _int_value;
        double _float_value;
        bool _bool_value;
        std::chrono::time_point<std::chrono::system_clock> _time;
        ConditionType &_type;   ///Type of this condition
    };
}

#endif //RCDB_CPP_CONDITION_H

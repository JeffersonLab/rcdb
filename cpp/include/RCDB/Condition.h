//
// Created by romanov on 1/28/16.
//

#ifndef RCDB_CPP_CONDITION_H
#define RCDB_CPP_CONDITION_H

#include "ConditionType.h"
#include "Exceptions.h"
#include <chrono>
#include <string>
#include "rapidjson/document.h"

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
                GetValueType() != ValueTypes::Blob) {
                throw rcdb::ValueFormatError("Value type of the condition is not String, Json or Blob");
            }

            return _text_value;
        }


        /// @deprecated use json ToJson() instead
        rapidjson::Document ToJsonDocument()
        {
            using namespace rapidjson;

            if (GetValueType() != ValueTypes::Json) {
                throw rcdb::ValueFormatError("Value type of the condition is not Json");
            }

            Document document;  // Default template parameter uses UTF8 and MemoryPoolAllocator.


            // "normal" parsing, decode strings to new buffers. Can use other input stream via ParseStream().
            if (document.Parse(_text_value.c_str()).HasParseError()) {
                throw rcdb::ValueFormatError("Error while parsing JSon");
            }

            return document;
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


        void SetId(unsigned long _id) {
            Condition::_id = _id;
        }

        unsigned long GetId() {
            return _id;
        }

        void SetRunNumber(unsigned long _runNumber) {
            Condition::_runNumber = _runNumber;
        }

        void SetTextValue(const std::string &_text_value) {
            Condition::_text_value = _text_value;
        }

        void SetIntValue(int _int_value) {
            Condition::_int_value = _int_value;
        }

        void SetFloatValue(double _float_value) {
            Condition::_float_value = _float_value;
        }

        void SetBoolValue(bool _bool_value) {
            Condition::_bool_value = _bool_value;
        }

        void SetTime(std::chrono::time_point<std::chrono::system_clock> _time) {
            Condition::_time = _time;
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

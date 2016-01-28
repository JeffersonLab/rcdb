//
// Created by romanov on 1/28/16.
//

#ifndef RCDB_CPP_CONDITION_H
#define RCDB_CPP_CONDITION_H

#include "ConditionType.h"
#include "Exceptions.h"
#include <chrono>
#include <string>

class DataProvder;

namespace rcdb
{

    class Condition {
    public:
        Condition(ConditionType &conditionType) :
                _type(conditionType) {

        }

        /**
         * Returns the type @see(rcdb::ValueTypes) of the value of this condition
         */
        rcdb::ValueTypes GetValueType() { return _type.GetValueType(); }


        template <class T>
                T GetValue()
        {
                throw rcdb::ValueFormatError("This type is not supported. Use GetValueType() to see the type of this condition value");

        }

        template <>  int GetValue<int>() {

                if(GetValueType() != ValueTypes::Int) {
                        throw rcdb::ValueFormatError("Value type of the condition is not int");
                }
                return _int_value;
        }

        template <>  bool GetValue<bool>() {

            if(GetValueType() != ValueTypes::Bool) {
                throw rcdb::ValueFormatError("Value type of the condition is not bool");
            }
            return _int_value;
        }

        template <>  double GetValue<double>() {

                if(GetValueType() != ValueTypes::Int && GetValueType() != ValueTypes::Float) {
                        throw rcdb::ValueFormatError("Value type of the condition is not 'Float'(double in C++) or int");
                }

                if(GetValueType() == ValueTypes::Int) return _int_value;

                return _float_value;
        }

        template <>  std::string GetValue<std::string>() {

                if(GetValueType() != ValueTypes::Json &&
                   GetValueType() != ValueTypes::String &&
                   GetValueType() != ValueTypes::Blob) {
                        throw rcdb::ValueFormatError("Value type of the condition is not String, Json or Blob");
                }

                return _text_value;
        }

        template <>  std::chrono::time_point<std::chrono::system_clock>
            GetValue<std::chrono::time_point<std::chrono::system_clock>>() {

            if(GetValueType() != ValueTypes::Time) {
                throw rcdb::ValueFormatError("Value type of the condition is not Time");
            }

            return _time;
        }


        void SetId(unsigned long _id) {
            Condition::_id = _id;
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

        void SetTime(const std::chrono::time_point<std::chrono::system_clock> &_time) {
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
        ConditionType& _type;   ///Type of this condition
    };
}


#endif //RCDB_CPP_CONDITION_H

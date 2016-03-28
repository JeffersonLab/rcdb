//
// Created by romanov on 1/28/16.
//

#ifndef RCDB_CPP_EXCEPTIONS_H
#define RCDB_CPP_EXCEPTIONS_H

#include <exception>
#include <stdexcept>

namespace rcdb
{
    /**
    * Value format error is thrown when you try to read value of Condition using the wrong type
    */
    class ValueFormatError: public std::logic_error
    {
    public:
        explicit ValueFormatError(const char* message): logic_error(message) {}
        explicit ValueFormatError(const std::string& message): logic_error(message) {}
    };

    /**
    * Value format error is thrown when you try to read value of Condition using the wrong type
    */
    class ConnectionStringError: public std::logic_error
    {
    public:
        explicit ConnectionStringError(const char* message): logic_error(message) {}
        explicit ConnectionStringError(const std::string& message): logic_error(message) {}
    };
}


#endif //RCDB_CPP_EXCEPTIONS_H

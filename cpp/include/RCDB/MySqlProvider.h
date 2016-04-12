//
// Created by romanov on 1/23/16.
//

#ifndef RCDB_CPP_MYSQLRCDBCONNECTION_H
#define RCDB_CPP_MYSQLRCDBCONNECTION_H

//#include <mysql/my_global.h>
#include <mysql.h>
#include <exception>
#include <stdexcept>
#include "DataProvider.h"
#include "MySqlConnectionInfo.h"
#include "Exceptions.h"

namespace rcdb {
    class MySqlProvider : public DataProvider {
    public:
        MySqlProvider(std::string connectionString) : DataProvider(),
                          _connection(mysql_init(NULL), &mysql_close)
        {
            using namespace std;

            if (_connection.get() == nullptr) {
                throw logic_error("MySQL connection is NULL. Low memory?");
            }
            auto connectionInfo = ParseConnectionString(connectionString);


            // Connect to database
            auto connect_result = mysql_real_connect(_connection.get(),
                                                     connectionInfo.HostName.c_str(),
                                                     connectionInfo.UserName.c_str(),
                                                     connectionInfo.Password.c_str(),
                                                     connectionInfo.Database.c_str(),
                                                     connectionInfo.Port, NULL, 0);

            if ( connect_result == nullptr) {
                throw logic_error(mysql_error(_connection.get()));
            }

            // Query condition types
            if (mysql_query(_connection.get(), "SELECT id,name,value_type FROM condition_types")) {
                throw logic_error(mysql_error(_connection.get()));
            }

            unique_ptr<MYSQL_RES, void (*)(MYSQL_RES*)>
                    result(mysql_store_result(_connection.get()), &mysql_free_result);

            if (!result) {
                throw logic_error(mysql_error(_connection.get()));
            }

            // Iterate the results and fill ConditionType objects list
            MYSQL_ROW row;
            while ((row = mysql_fetch_row(result.get()))) {
                    auto id = std::stoul(row[0]);
                    const string name(row[1]); // = query.getColumn(1).getText();
                    const string typeStr(row[2]); // .getColumn(1).getBytes();

                    ConditionType conditionType;
                    conditionType.SetId(id);
                    conditionType.SetName(name);
                    conditionType.SetValueType(ConditionType::StringToValueType(typeStr));
                    _types.push_back(conditionType);
                    _typesByName[name]=conditionType;
            }
        }

        MySqlProvider(MySqlProvider &&) = default;                    // Move constructor
        MySqlProvider &operator=(MySqlProvider &&) & = default;       // Move assignment operator
        virtual ~MySqlProvider() override { }

        /** Gets conditions by ConditionType and run (@see GetRun and SetRun) */
        virtual std::unique_ptr<Condition> GetCondition(uint64_t runNumber, const ConditionType& cndType) override
        {
            using namespace std;

            // id:0, bool_value:1, float_value:2, int_value:3, text_value:4, time_value:5
            static const int bool_column = 1;
            static const int float_column = 2;
            static const int int_column = 3;
            static const int text_column = 4;
            static const int time_column = 5;
            uint64_t typeId = cndType.GetId();
            uint64_t run = runNumber;

            string query = string("SELECT id, bool_value, float_value, int_value, text_value, time_value FROM conditions WHERE run_number =") +
                           to_string(runNumber) +
                           string(" AND condition_type_id = ") +
                           to_string(cndType.GetId());

            // Query condition types
            if (mysql_query(_connection.get(), query.c_str())) {

                throw logic_error(mysql_error(_connection.get()));
            }

            unique_ptr<MYSQL_RES, void (*)(MYSQL_RES*)>
                    result(mysql_store_result(_connection.get()), &mysql_free_result);

            if (!result) {
                throw logic_error(mysql_error(_connection.get()));
            }

            // Iterate the results and fill ConditionType objects list
            MYSQL_ROW row;
            while ((row = mysql_fetch_row(result.get()))) {
                auto id = stoul(row[0]);
                std::unique_ptr<Condition> condition(new Condition((ConditionType &) cndType));
                condition->SetId(id);

                switch (cndType.GetValueType()) {
                    case ValueTypes::Bool:
                        if(row[bool_column] == nullptr) return std::unique_ptr<Condition>();
                        condition->SetBoolValue((bool)stoi(row[bool_column]));
                        return condition;
                    case ValueTypes::Json:
                    case ValueTypes::String:
                    case ValueTypes::Blob:
                        if(row[text_column] == nullptr) return std::unique_ptr<Condition>();
                        condition->SetTextValue(string(row[text_column]));
                        return condition;
                    case ValueTypes::Float:
                        if(row[float_column] == nullptr) return std::unique_ptr<Condition>();
                        condition->SetFloatValue(stod(row[float_column]));
                        return condition;
                    case ValueTypes::Int:
                        if(row[int_column] == nullptr) return std::unique_ptr<Condition>();
                        condition->SetIntValue(stoi(row[int_column]));
                        return condition;
                    case ValueTypes::Time:
                        if(row[time_column] == nullptr) return std::unique_ptr<Condition>();
                        condition->SetTime(
                                chrono::system_clock::from_time_t(stoul(row[int_column])));
                        return condition;
                    default:
                        throw std::logic_error("ValueTypes type is something different than one of possible values");
                }
            }

            return std::unique_ptr<Condition>(); //Empty ptr
        }

        /** Gets conditions by name and run (@see GetRun and SetRun) */
        std::unique_ptr<Condition> GetCondition(uint64_t runNumber, const std::string& name)
        {
            return GetCondition(runNumber, _typesByName[name]);
        }

        void Test() {
            std::unique_ptr<MYSQL, void (*)(MYSQL*)> con(mysql_init(NULL), &mysql_close);

            if (con == NULL) {
                throw std::logic_error(std::string(""));
            }

            if (mysql_real_connect(con.get(), "localhost", "rcdb", "", "rcdb", 0, NULL, 0) == NULL) {
                throw std::logic_error(mysql_error(con.get()));
            }

            if (mysql_query(con.get(), "SELECT id,name,value_type FROM condition_types")) {
                throw std::logic_error(mysql_error(con.get()));
            }

            std::unique_ptr<MYSQL_RES, void (*)(MYSQL_RES*)>
                    result(mysql_store_result(con.get()), &mysql_free_result);


            if (!result) {
                throw std::logic_error(mysql_error(con.get()));
            }

            int num_fields = mysql_num_fields(result.get());

            MYSQL_ROW row;

            while ((row = mysql_fetch_row(result.get()))) {
                for (int i = 0; i < num_fields; i++) {
                    printf("%s ", row[i] ? row[i] : "NULL");
                }
                printf("\n");
            }

            (result);
            (con);
        }

        static MySQLConnectionInfo ParseConnectionString(std::string conStr)
        {
            using namespace std;

            MySQLConnectionInfo connection;

            //first check for uri type
            auto typePos = conStr.find("mysql://");
            if(typePos==string::npos) {
                throw ConnectionStringError("ERROR. MySql connection string must begin with 'mysql://'");
            }

            //ok we don't need mysql:// in the future. Moreover it will mess our separation logic
            conStr.erase(0,8);

            //then if there is '@' that separates login/password part of uri
            auto atPos = conStr.find('@');
            if(atPos!=string::npos) {
                string logPassStr;

                //ok! we have it!
                //take it... but with caution
                if(atPos == conStr.length()-1) {
                    //it is like 'login:pwd@' string
                    logPassStr = conStr.substr(0, atPos);
                    conStr=string("");
                }
                else if(atPos==0) {
                    //it is like '@localhost' string
                    conStr=conStr.substr(1);
                    logPassStr = string("");
                }
                else {
                    //a regular case
                    logPassStr = conStr.substr(0,atPos);
                    conStr=conStr.substr(atPos+1);
                }

                //is it only login or login&&password?
                auto colonPos = logPassStr.find(':');
                if(colonPos!=string::npos) {
                    connection.UserName = logPassStr.substr(0,colonPos);
                    connection.Password = logPassStr.substr(colonPos+1);
                }
                else {
                    connection.UserName = logPassStr;
                }
            }

            //ok, now we have only "address:port database" part of the string

            //1) deal with database;
            auto whitePos=conStr.find('/');
            if(whitePos!=string::npos) {
                connection.Database = conStr.substr(whitePos+1);
                conStr.erase(whitePos);
            }

            //2) deal with port
            auto colonPos = conStr.find(':');
            if(colonPos!=string::npos) {
                string portStr=conStr.substr(colonPos+1);
                conStr.erase(colonPos);

                connection.Port = (unsigned int) stol(portStr.c_str());
            }

            //3) everything that is last would be address
            connection.HostName = conStr;

            return connection;
        }

    protected:


    private:
        std::unique_ptr<MYSQL, void (*)(MYSQL*)> _connection;

        MySqlProvider(const MySqlProvider &) = delete;               // disable Copy constructor
        MySqlProvider &operator=(const MySqlProvider &) = delete;    // disable Copy assignment
    };
}


#endif //RCDB_CPP_MYSQLRCDBCONNECTION_H

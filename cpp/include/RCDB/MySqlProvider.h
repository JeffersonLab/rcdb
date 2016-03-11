//
// Created by romanov on 1/23/16.
//

#ifndef RCDB_CPP_MYSQLRCDBCONNECTION_H
#define RCDB_CPP_MYSQLRCDBCONNECTION_H

//#include <mysql/my_global.h>
#include <mysql/mysql.h>
#include <exception>
#include <stdexcept>
#include "DataProvider.h"
#include "MySqlConnectionInfo.h"
#include "Exceptions.h"

namespace rcdb {


    class MySqlProvider : public DataProvider {
    public:
        MySqlProvider() : DataProvider(),
                          _connection(mysql_init(NULL), &mysql_close)
        {

        }

        MySqlProvider(MySqlProvider &&) = default;                    // Move constructor
        MySqlProvider &operator=(MySqlProvider &&) & = default;       // Move assignment operator
        virtual ~MySqlProvider() override { }

        virtual std::unique_ptr<Condition> GetCondition(const ConditionType& cndType) override
        {
            return std::unique_ptr<Condition>();
        }

        // ...

        friend void swap(MySqlProvider &first, MySqlProvider &second) // nothrow
        {
            // enable ADL (not necessary in our case, but good practice)
            using std::swap;

            // by swapping the members of two classes,
            // the two classes are effectively swapped
//            swap(first.mSize, second.mSize);
            //          swap(first.mArray, second.mArray);
        }


        void Test() {
            std::unique_ptr<MYSQL, void (*)(MYSQL*)> con(mysql_init(NULL), &mysql_close);

            if (con == NULL) {
                throw std::logic_error(mysql_error(con.get()));
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
            int typePos = conStr.find("mysql://");
            if(typePos==string::npos)
            {
                throw MySqlConnectionStringError("ERROR. MySql connection string must begin with 'mysql://'");
            }

            //ok we don't need mysql:// in the future. Moreover it will mess our separation logic
            conStr.erase(0,8);

            //then if there is '@' that separates login/password part of uri
            int atPos = conStr.find('@');
            if(atPos!=string::npos)
            {
                string logPassStr;

                //ok! we have it!
                //take it... but with caution
                if(atPos == conStr.length()-1)
                {
                    //it is like 'login:pwd@' string
                    logPassStr = conStr.substr(0, atPos);
                    conStr=string("");
                }
                else if(atPos==0)
                {
                    //it is like '@localhost' string
                    conStr=conStr.substr(1);
                    logPassStr = string("");
                }
                else
                {
                    //a regular case
                    logPassStr = conStr.substr(0,atPos);
                    conStr=conStr.substr(atPos+1);
                }

                //is it only login or login&&password?
                int colonPos = logPassStr.find(':');
                if(colonPos!=string::npos)
                {
                    connection.UserName = logPassStr.substr(0,colonPos);
                    connection.Password = logPassStr.substr(colonPos+1);
                }
                else
                {
                    connection.UserName = logPassStr;
                }
            }

            //ok, now we have only "address:port database" part of the string

            //1) deal with database;
            int whitePos=conStr.find('/');
            if(whitePos!=string::npos)
            {
                connection.Database = conStr.substr(whitePos+1);
                conStr.erase(whitePos);
            }

            //2) deal with port
            int colonPos = conStr.find(':');
            if(colonPos!=string::npos)
            {
                string portStr=conStr.substr(colonPos+1);
                conStr.erase(colonPos);

                connection.Port =atoi(portStr.c_str());
            }

            //3) everything that is last whould be address
            connection.HostName = conStr;

            return connection;
        }

    protected:


    private:
        std::unique_ptr<MYSQL, void (*)(MYSQL*)> _connection;


        MySqlProvider(const MySqlProvider &);               // disable Copy constructor
        MySqlProvider &operator=(const MySqlProvider &);   // Copy assignment operator

    };
}


#endif //RCDB_CPP_MYSQLRCDBCONNECTION_H

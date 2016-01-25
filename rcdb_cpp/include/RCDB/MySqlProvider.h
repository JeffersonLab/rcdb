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

        void GetData() override {

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

    protected:
        void LoadConditionTypes() override {
        }


    private:
        std::unique_ptr<MYSQL, void (*)(MYSQL*)> _connection;


        MySqlProvider(const MySqlProvider &);               // disable Copy constructor
        MySqlProvider &operator=(const MySqlProvider &);   // Copy assignment operator

    };
}


#endif //RCDB_CPP_MYSQLRCDBCONNECTION_H

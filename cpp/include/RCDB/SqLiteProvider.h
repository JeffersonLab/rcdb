//
// Created by romanov on 1/23/16.
//

#ifndef RCDB_CPP_SQLITEPROVIDER_H
#define RCDB_CPP_SQLITEPROVIDER_H


#include <SQLiteCpp/SQLiteCpp.h>
#include <iostream>
#include "DataProvider.h"

namespace rcdb {
    class SqLiteProvider : public DataProvider {
    public:
        SqLiteProvider(std::string dbPath) throw :
                DataProvider(),
                _db(dbPath),
                _getConditionQuery(_db, "SELECT id, bool_value, float_value, int_value, text_value, time "
                                        "FROM conditions WHERE run_number = ? AND condition_type_id = ?")
        {
            //Fill types
            SQLite::Statement query(_db, "SELECT id, name, value_type FROM condition_types");


            while (query.executeStep()) {
                const int id = query.getColumn(0);
                const std::string name = query.getColumn(1); // = query.getColumn(1).getText();
                const std::string typeStr = query.getColumn(2); // .getColumn(1).getBytes();

                ConditionType conditionType;
                conditionType.SetId(id);
                conditionType.SetName(name);
                conditionType.SetValueType(ConditionType::StringToValueType(typeStr));
                _types.push_back(conditionType);
                _nameTypeMap[name]=conditionType;
            }
        }

        SqLiteProvider(SqLiteProvider &&) = default;                    // Move constructor

        SqLiteProvider &operator=(SqLiteProvider &&) & = default;       // Move assignment operator
        virtual ~SqLiteProvider() {

        }                     // Destructor

        /** Gets conditions by name and run (@see GetRun and SetRun) */
        virtual Condition GetCondition(const std::string& name) override
        {

        }

        void Test() {
            // Open a database file in readonly mode
            SQLite::Database db("/home/romanov/gluex/rcdb/rcdb_2016-01-28.sqlite.db");  // SQLITE_OPEN_READONLY

            std::cout << "SQLite database file '" << db.getFilename().c_str() << "' opened successfully\n";

            ///// a) Loop to get values of column by index, using auto cast to variable type

            // Compile a SQL query, containing one parameter (index 1)
            SQLite::Statement query(db, "SELECT id, name, value_type FROM condition_types WHERE id > ?");
            std::cout << "SQLite statement '" << query.getQuery().c_str() << "' compiled (" << query.getColumnCount() <<
            " columns in the result)\n";

            // Bind the integer value 2 to the first parameter of the SQL query
            query.bind(1, 5);
            std::cout << "binded with integer value '5' :\n";

            // Loop to execute the query step by step, to get one a row of results at a time
            while (query.executeStep()) {
                // Demonstrates how to get some typed column value (and the equivalent explicit call)
                const int id = query.getColumn(0); // = query.getColumn(0).getInt();
                //const char*       pvalue = query.getColumn(1); // = query.getColumn(1).getText();
                const std::string name = query.getColumn(1); // = query.getColumn(1).getText();
                const std::string type = query.getColumn(2); // .getColumn(1).getBytes();

                std::cout << "row (" << id << ", \"" << name.c_str() << "\"(" << type << ") " << ")\n";
            }

            ///// b) Get aliased column names (and original column names if possible)

            // Reset the query to use it again
            query.reset();
        }

    protected:
        void LoadConditionTypes() override {
        }

    private:
        SqLiteProvider(const SqLiteProvider &);             // disable Copy constructor
        SqLiteProvider &operator=(const SqLiteProvider &);  // disable Copy assignment operator

        SQLite::Database _db;
        SQLite::Statement _getConditionQuery;
    };
}

#endif //RCDB_CPP_SQLITEPROVIDER_H

//
// Created by romanov on 3/28/16.
//

#ifndef RCDB_CPP_CONNECTION_H
#define RCDB_CPP_CONNECTION_H

#include <string>
#include <memory>
#include "DataProvider.h"
#include "SqLiteProvider.h"
#include "MySqlProvider.h"
#include <mutex>

namespace rcdb{

    class Connection{
    public:
        /** Default constructor */
        Connection(std::string connectionStr, bool immediateConnect= true):
                _connectionString(connectionStr)
        {

            if (immediateConnect){
                Connect();
            }
        }

        void Connect()
        {
            std::lock_guard<std::mutex> guard(_mutex);

            if(_connectionString.find("sqlite:///") == 0)
            {
                _provider.reset(new SqLiteProvider(_connectionString));
            }
            else
            {
                _provider.reset(new MySqlProvider(_connectionString));
            }


        }



    private:
        std::string _connectionString;
        std::unique_ptr<DataProvider> _provider;
        std::mutex _mutex;    /// This class  uses this mutex



        Connection(const Connection &) = delete;               // disable Copy constructor
        Connection &operator=(const Connection &) = delete;    // disable Copy assignment

    };

}

#endif //RCDB_CPP_CONNECTION_H

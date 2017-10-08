//
// Created by romanov on 3/28/16.
//

#ifndef RCDB_CPP_CONNECTION_H
#define RCDB_CPP_CONNECTION_H

#include <stdexcept>
#include <string>
#include <memory>
#include <mutex>

#include "DataProvider.h"

#ifdef RCDB_SQLITE
    #include "SqLiteProvider.h"
#endif

#ifdef RCDB_MYSQL
   #include "MySqlProvider.h"
#endif


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

            if(_connectionString.find("sqlite:///") == 0) {
                #ifdef RCDB_SQLITE
                    _provider.reset(new SqLiteProvider(_connectionString));
                #else
                    throw std::logic_error("RCDB built without SQLite3 support. Rebuild it using 'with-sqlite=true' flag");
                #endif
            }
            else if(_connectionString.find("mysql://") == 0){

                #ifdef RCDB_MYSQL
                    _provider.reset(new MySqlProvider(_connectionString));
                #else                
                    throw std::logic_error("RCDB built without MySQL support. Rebuild it using 'with-mysql=true' flag");
                #endif
            }
            else{
                throw ConnectionStringError("ERROR. Connection string must begin with 'mysql://' or sqlite:///");
            }
        }

        bool IsConnected()
        {
            std::lock_guard<std::mutex> guard(_mutex);
            return _provider.get() != nullptr;
        }

        void Close()
        {
            std::lock_guard<std::mutex> guard(_mutex);
            _provider.reset();
        }

        /** Gets conditions by name and run (@see GetRun and SetRun) */
        std::unique_ptr<Condition> GetCondition(uint64_t runNumber, const ConditionType& cndType)
        {
            return _provider->GetCondition(runNumber, cndType);
        }

        /** Gets conditions by name and run (@see GetRun and SetRun) */
        std::unique_ptr<Condition> GetCondition(uint64_t runNumber, const std::string& name)
        {
            return _provider->GetCondition(runNumber, name);
        }

        /** Gets file (with content) by name and run (@see GetRun and SetRun) */
        std::unique_ptr<RcdbFile> GetFile(uint64_t runNumber, const std::string& name)
        {
            return _provider->GetFile(runNumber, name);
        }

        virtual std::vector<std::string> GetFileNames(uint64_t runNumber)
        {
            return _provider->GetFileNames(runNumber);
        }

    protected:
        std::string _connectionString;
        std::unique_ptr<DataProvider> _provider;
        std::mutex _mutex;    /// This class  uses this mutex

    private:
        Connection(const Connection &) = delete;               // disable Copy constructor
        Connection &operator=(const Connection &) = delete;    // disable Copy assignment
    };
}

#endif //RCDB_CPP_CONNECTION_H

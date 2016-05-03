//
// Created by romanov on 3/28/16.
//

#ifndef RCDB_CPP_CONNECTION_H
#define RCDB_CPP_CONNECTION_H

#include <string>
#include <memory>
#include <mutex>

#include "DataProvider.h"
#include "SqLiteProvider.h"
#include "MySqlProvider.h"

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
                _provider.reset(new SqLiteProvider(_connectionString));
            }
            else {
                _provider.reset(new MySqlProvider(_connectionString));
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

        uint64_t GetRun() const {
            return _run;
        }

        void SetRun(uint64_t run) {
            _run = run;
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


    private:
        std::string _connectionString;
        std::unique_ptr<DataProvider> _provider;
        std::mutex _mutex;    /// This class  uses this mutex


        uint64_t _run;
        Connection(const Connection &) = delete;               // disable Copy constructor
        Connection &operator=(const Connection &) = delete;    // disable Copy assignment

    };

}

#endif //RCDB_CPP_CONNECTION_H

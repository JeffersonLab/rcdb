//
// Created by romanov on 3/28/16.
//

#ifndef RCDB_CPP_WRITING_CONNECTION_H
#define RCDB_CPP_WRITING_CONNECTION_H

#include "Connection.h"

#ifdef RCDB_MYSQL
   #include "MySqlProvider.h"
#endif


namespace rcdb{

    class WritingConnection: public Connection {
    public:
        WritingConnection(std::string connectionStr, bool immediateConnect= true):
                Connection(connectionStr, immediateConnect)
        {

        }

        void AddRun(uint64_t runNumber)
        {
            ((MySqlProvider*)_provider.get())->AddRun(runNumber);
        }

        void AddRunStartTime(uint64_t runNumber, std::tm time)
        {
            ((MySqlProvider*)_provider.get())->AddRunStartTime(runNumber, time);
        }

        void AddRunEndTime(uint64_t runNumber, std::tm time)
        {
            ((MySqlProvider*)_provider.get())->AddRunEndTime(runNumber, time);
        }


        void AddCondition(uint64_t runNumber, const std::string& name, long value )
        {
            ((MySqlProvider*)_provider.get())->AddCondition(runNumber, name, value);
        }

        void AddCondition(uint64_t runNumber, const std::string& name, std::tm value )
        {
            ((MySqlProvider*)_provider.get())->AddCondition(runNumber, name, value);
        }

        void AddCondition(uint64_t runNumber, const std::string& name, double value )
        {
            ((MySqlProvider*)_provider.get())->AddCondition(runNumber, name, value);
        }

        void AddCondition(uint64_t runNumber, const std::string& name, const std::string& value)
        {
            ((MySqlProvider*)_provider.get())->AddCondition(runNumber, name, value);
        }

        void AddCondition(uint64_t runNumber, const std::string& name, bool value)
        {
            ((MySqlProvider*)_provider.get())->AddCondition(runNumber, name, value);
        }

    private:
    };
}

#endif //RCDB_CPP_WRITING_CONNECTION_H

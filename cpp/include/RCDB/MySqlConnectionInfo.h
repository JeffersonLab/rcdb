#ifndef RCDB_CPP_MYSQLCONNECTIONINFO_H
#define RCDB_CPP_MYSQLCONNECTIONINFO_H

#include <string>


namespace rcdb
{
    ///Internal temporary class to pass connection info to mysql provider
    class MySQLConnectionInfo
    {
    public:
        MySQLConnectionInfo()
                :UserName(""),
                 Password(""),
                 HostName(""),
                 Database(""),
                 Port(0)
        {
        }
        ~MySQLConnectionInfo(){}
        std::string	UserName;
        std::string	Password;
        std::string Database;
        std::string	HostName;
        int		Port;

    };

}
#endif //RCDB_CPP_MYSQLCONNECTIONINFO_H

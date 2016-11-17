#ifndef RCDB_CPP_MYSQLCONNECTIONINFO_H
#define RCDB_CPP_MYSQLCONNECTIONINFO_H

#include <string>


namespace rcdb
{
    ///Internal temporary class to pass MySQL connection info to mysql provider
    class MySQLConnectionInfo
    {
    public:
        MySQLConnectionInfo()
                :UserName(""),
                 Password(""),
                 Database(""),
                 HostName(""),
                 Port(0)
        {
        }
        ~MySQLConnectionInfo(){}
        std::string	UserName;
        std::string	Password;
        std::string Database;
        std::string	HostName;
        unsigned int		Port;

    };

}
#endif //RCDB_CPP_MYSQLCONNECTIONINFO_H

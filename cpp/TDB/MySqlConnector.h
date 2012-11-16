#include <my_global.h>
#include <mysql.h>
#include <string>
#include <vector>

#include "Error.h"

using namespace std;
#pragma once

namespace tdb
{


class MySqlConnector
{
public:

    MySqlConnector(void)
    {
        _conn = NULL;
    }

    ~MySqlConnector(void)
    {
        if(IsConnected()) Disconnect();
    }

    /** @brief Connects to MySql database
     *
     * @param[in]  const string & host
     * @param[in]  const string & user
     * @param[in]  const string & passwd
     * @param[in]  const string & db
     * @param[in]  unsigned int port
     * @param[in]  const string & unix_socket
     * @param[in]  unsigned long clientflag
     * @return   bool
     */
    virtual Error * Connect( const char* host, const char* user, const char* passwd, const char* database, unsigned int port = 0, const char* unix_socket = NULL, unsigned long clientflag = 0)
    {
        string fname("tdb::MySqlConnector::Connect(...)");

        if(IsConnected()) return new Error(" Error. " + fname + " Already connected to database");

        _conn = mysql_init(NULL);
        
        //create connection object
        if(!_conn) return new Error(" Error. " + fname + " Unable to create MySQL connection object");
        
        //connect!
        if(!mysql_real_connect(_conn, host , user , passwd , database, port, unix_socket, clientflag))
        {
            return new Error(" Error. " + fname + " Failed to connect to database. " + GetLastMySqlErrorDescription());
        }

        
        return NULL; //No errors!
    }


    
    /** @brief executes a select query and fills outTable with query result
     *
     * @param[out]  vector<vector<string> > & outTable - strings table to fill 
     * @param[in]   const string & query - query to execute
     * @return   NULL if no errors or Error*
     */
    Error* QuerySelect(vector<vector<string> > &outTable, const string & query)
    {
        string fname("tdb::MySqlConnector::QuerySelect(...)");

        if(!IsConnected())
        {
             return new Error(" Error. " + fname + " Connection is not opened. ");
        }

        //execute query
        if(mysql_query(_conn, query.c_str()))
        {
            return new Error(" Error. " + fname + " Failed to execute query. " + GetLastMySqlErrorDescription());
        }

        //store query result
        MYSQL_RES* result = mysql_store_result(_conn);
        if(!result)
        {
            return new Error(" Error. " + fname + "Failed to store query result. " + GetLastMySqlErrorDescription());
        }
        
        //iterate through fields
        int num_fields = mysql_num_fields(result);
        outTable.clear();
        MYSQL_ROW row;
        while (row = mysql_fetch_row(result))
        {
            vector<string> fields;
            for(int i = 0; i < num_fields; i++)
            {
                fields.push_back(string(row[i] ? row[i] : ""));
            }
            outTable.push_back(fields);
        }

        //free results
        mysql_free_result(result);

        mQuerry = string(query);

        //NULL === No errors
        return NULL;
    }

    /**
	 * @brief indicates ether the connection is open or not
	 * 
	 * @return true if  connection is open
	 */
	bool IsConnected() { return _conn ? true: false; }
	
	/**
	 * @brief closes connection to data
	 */
	Error *  Disconnect()
    {
        if(!IsConnected()) 
        {
            return new Error("Error. tdb::MySqlConnector::Disconnect Can't disconnect since no connection is opened");
        }
        mysql_close(_conn);
        _conn = NULL;
        return NULL;
    }

protected:
    /** @brief Gets Last MySql Error Description number and other string. 
     * 
     * Is used for creating tdb::Error object
     *
     * @return   std::string
     */
    string GetLastMySqlErrorDescription()
    {
        return  "MySql error: " + string(mysql_error(_conn));
    }
    
private:
     MYSQL *_conn;
     string mQuerry;   //full text of last full get assignment query
};

}
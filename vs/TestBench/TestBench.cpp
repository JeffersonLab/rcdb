#include <my_global.h>
#include <mysql.h>
#include <iostream>
#include <vector>
#include "TDB/MySqlConnector.h"

#include "TDB/Error.h"

#define TDB_NEW_ERROR( msg, inex) new tdb::Error(msg, " file: "##__FILE__##"\n line: "##__LINE__, inex)


using namespace tdb;

std::string string_format(const std::string &fmt, ...) {
    int size=100;
    std::string str;
    va_list ap;
    while (1) {
        str.resize(size);
        va_start(ap, fmt);
        int n = vsnprintf((char *)str.c_str(), size, fmt.c_str(), ap);
        va_end(ap);
        if (n > -1 && n < size) {
            str.resize(n);
            return str;
        }
        if (n > -1)
            size=n+1;
        else
            size*=2;
    }
}

int main(int argc, char **argv)
{
    tdb::MySqlConnector conn;    
    
    if(auto error = conn.Connect("127.0.0.1", "triggerdb", "", "triggerdb", 0, NULL, 0)) 
    {
        cout<<error->Message()<<endl;
        return 1;
    }

    vector<vector<string> > table; 

    if(auto error = conn.QuerySelect(table, "SELECT * from boards")) 
    {
        cout<<error->Message()<<endl;
        return 1;
    }

    for(int row=0; row<table.size(); row++)
    {
        for(int col=0; col<table[0].size(); col++)
        {
            cout<<table[row][col]<<"\t";
        }
        cout<<endl;
    }
}
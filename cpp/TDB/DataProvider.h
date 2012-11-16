#include <my_global.h>
#include <mysql.h>
#include <string>
#include <vector>

#include "Error.h"
#include "TDB/MySqlConnector.h"
#include "TDB/BoardFactory.h"
#include "TDB/Board.h"

using namespace std;
#pragma once

namespace tdb
{


class DataProvider
{
public:

    DataProvider(void):
        _database(new MySqlConnector()),
        _boardFactory(new BoardFactory(_database))
    {
    }

    ~DataProvider(void)
    {   
    }

    shared_ptr<MySqlConnector> Database() const { return _database; }
    shared_ptr<BoardFactory> Boards() const { return _boardFactory; }

protected:
    
    
private:
     DataProvider(DataProvider& prov);
     shared_ptr<MySqlConnector> _database;     
     
     shared_ptr<BoardFactory> _boardFactory;
     
};

}
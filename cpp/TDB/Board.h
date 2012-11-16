#include <string>
#include <vector>

#include "Error.h"

using namespace std;
#pragma once


namespace tdb
{

class BoardFactory;



class Board
{
     friend BoardFactory;

public:

    Board(void)
    {
        
    }

    ~Board(void)
    {
        
    }

    int DatabaseId() const { return _databaseId; }
    std::string BoardType() const { return _boardType; }
    std::string Name() const { return _name; }
    std::string Serial() const { return _serial; }

protected:
    
    
private:
    void DatabaseId(int val) { _databaseId = val; }
    void BoardType(std::string val) { _boardType = val; }
    void Name(std::string val) { _name = val; }
    void Serial(std::string val) { _serial = val; }

    int _databaseId;    
    string _boardType;    
    string _name;   
    string _serial;
};

typedef vector<shared_ptr<tdb::Board>> board_vector;

}
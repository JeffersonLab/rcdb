
#include <string>
#include <vector>

#include "Error.h"
#include "TDB/MySqlConnector.h"
#include "TDB/Board.h"
#include "TDB/StringUtils.h"

using namespace std;
#pragma once

namespace tdb
{


class BoardFactory
{
public:

    BoardFactory(const shared_ptr<MySqlConnector>& connector):
        _database(connector)
    {
    }

    ~BoardFactory(void)
    {
        
    }


    /** @brief Load all boards records from database
     *
     * @param[out]  vector<shared_ptr<Board>> array of records that will be filled
     * @return   Error*
     */
    Error* LoadBoards(board_vector& outBoards)
    {
        outBoards.clear();
        vector<vector<string> > sqlResult;
        if(auto error = _database->QuerySelect(sqlResult, "SELECT id, board_type, name, serial FROM boards"))
        {
            return new Error("Error in BoardFactory::LoadBoards(...). Unable to load boards. ", error);
        }

        //Do we have records?
        if(sqlResult.size()<=0)
        {
            return new Error("Error in BoardFactory::LoadBoards(...). Database returned no boards");
        }
        
        for(int row = 0 ; row<sqlResult.size(); row++)
        {
            //Create board and put it
            auto board = new Board();
            outBoards.push_back(shared_ptr<Board>(board));

            //parse board columns
            auto& strVals = sqlResult[row];
            
            //parse int
            try
            {
                board->DatabaseId(stoi(strVals[0]));
            }
            catch(std::exception& ex)
            {
                return new Error("Error in BoardFactory::LoadBoards(...). while parsing database id. string value '" + strVals[0] + "'. Parse error: " + string(ex.what()));
            }

            board->BoardType(strVals[1]);
            board->Name(strVals[2]);
            board->Serial(strVals[3]);            
        }

        return NULL;
    }

protected:
    
    
private:
     shared_ptr<MySqlConnector> _database;

     
};

}
//
// Created by romanov on 4/29/16.
//

#ifndef RCDB_CPP_RCDBFILE_H
#define RCDB_CPP_RCDBFILE_H

#include <cstdint>
#include <string>

namespace rcdb{

    class RcdbFile {
    public:
    private:
        uint64_t _id;
        std::string _name;
        std::string _content;

    };

}


#endif //RCDB_CPP_RCDBFILE_H

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

        RcdbFile(uint64_t id, std::string name, std::string sha256, std::string content):
            _id(id),
            _name(name),
            _sha256(sha256),
            _content(content)
        {

        }

        uint64_t GetId() const {
            return _id;
        }

        const std::string &GetName() const {
            return _name;
        }

        const std::string &GetContent() const {
            return _content;
        }

        const std::string &GetSha256() const {
            return _sha256;
        }


    private:
        uint64_t    _id;
        std::string _name;
        std::string _sha256;
        std::string _content;
    };

}


#endif //RCDB_CPP_RCDBFILE_H

//
// Created by romanov on 1/25/16.
//

#ifndef RCDB_CPP_DATAPROVIDER_H
#define RCDB_CPP_DATAPROVIDER_H

#include <vector>
#include <bits/stl_map.h>

#include "ConditionType.h"
#include "Condition.h"


namespace rcdb {

    class DataProvider {
    public:
        /** Gets conditions by name and run (@see GetRun and SetRun) */
        virtual Condition GetCondition(const std::string& name) = 0;

        uint64_t GetRun() const {
            return _run;
        }

        void SetRun(uint64_t _run) {
            DataProvider::_run = _run;
        }

    protected:


        virtual void LoadConditionTypes() = 0;

        DataProvider() { }

        DataProvider(const DataProvider &) = default;               // Copy constructor
        DataProvider(DataProvider &&) = default;                    // Move constructor
        DataProvider &operator=(const DataProvider &) & = default;  // Copy assignment operator
        DataProvider &operator=(DataProvider &&) & = default;       // Move assignment operator
        virtual ~DataProvider() { }                                 // Destructor

        std::vector<ConditionType> _types;                          /// Condition types
        std::map<std::string, ConditionType> _nameTypeMap;          /// Condition types mapped by name
        uint64_t _run;
    private:
        bool mAreConditionTypesLoaded;
    };


}

#endif //RCDB_CPP_DATAPROVIDER_H

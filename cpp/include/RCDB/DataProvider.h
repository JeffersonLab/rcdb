//
// Created by romanov on 1/25/16.
//

#ifndef RCDB_CPP_DATAPROVIDER_H
#define RCDB_CPP_DATAPROVIDER_H

#include <vector>
#include <memory>
#include <bits/stl_map.h>

#include "ConditionType.h"
#include "Condition.h"


namespace rcdb {

    class DataProvider {
    public:
        /** Gets conditions by conditionType (@see GetRun and SetRun) */
        virtual std::unique_ptr<Condition> GetCondition(const ConditionType& cndType) = 0;

        /** Gets conditions by name and run (@see GetRun and SetRun) */
        std::unique_ptr<Condition> GetCondition(const std::string& name)
        {
            return GetCondition(_typesByName[name]);
        }

        uint64_t GetRun() const {
            return _run;
        }

        void SetRun(uint64_t _run) {
            DataProvider::_run = _run;
        }

    protected:


        DataProvider() { }

        DataProvider(const DataProvider &) = default;               // Copy constructor
        DataProvider(DataProvider &&) = default;                    // Move constructor
        DataProvider &operator=(const DataProvider &) & = default;  // Copy assignment operator
        DataProvider &operator=(DataProvider &&) & = default;       // Move assignment operator
        virtual ~DataProvider() { }                                 // Destructor

        std::vector<ConditionType> _types;                          /// Condition types
        std::map<std::string, ConditionType> _typesByName;          /// Condition types mapped by name
        uint64_t _run;
    private:
        bool mAreConditionTypesLoaded;
    };


}

#endif //RCDB_CPP_DATAPROVIDER_H

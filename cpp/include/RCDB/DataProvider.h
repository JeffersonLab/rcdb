//
// Created by romanov on 1/25/16.
//

#ifndef RCDB_CPP_DATAPROVIDER_H
#define RCDB_CPP_DATAPROVIDER_H

#include <vector>

#include "ConditionType.h"


namespace rcdb {

    class DataProvider {
    public:

    protected:
        virtual void GetData() = 0;

        virtual void LoadConditionTypes() = 0;

        DataProvider() { }

        DataProvider(const DataProvider &) = default;               // Copy constructor
        DataProvider(DataProvider &&) = default;                    // Move constructor
        DataProvider &operator=(const DataProvider &) & = default;  // Copy assignment operator
        DataProvider &operator=(DataProvider &&) & = default;       // Move assignment operator
        virtual ~DataProvider() { }                                 // Destructor

        std::vector<ConditionType> _types;                          /// Condition types
        uint64_t _run;

    private:
        bool mAreConditionTypesLoaded;
    };


}

#endif //RCDB_CPP_DATAPROVIDER_H

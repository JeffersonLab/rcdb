//
// Created by romanov on 1/25/16.
//

#ifndef RCDB_CPP_DATAPROVIDER_H
#define RCDB_CPP_DATAPROVIDER_H

#include <vector>
#include <memory>
#include <map>

#include "ConditionType.h"
#include "Condition.h"
#include "RcdbFile.h"


namespace rcdb {

    class DataProvider {
    public:
        /** Gets conditions by conditionType (@see GetRun and SetRun) */
        virtual std::unique_ptr<Condition> GetCondition(uint64_t runNumber, const ConditionType& cndType) = 0;

        /** Gets file saved to database by run number and file name */
        virtual std::unique_ptr<RcdbFile> GetFile(uint64_t runNumber, const std::string& name) = 0;

        virtual std::vector<std::string> GetFileNames(uint64_t runNumber) = 0;

        /** Gets conditions by name and run (@see GetRun and SetRun) */
        std::unique_ptr<Condition> GetCondition(uint64_t runNumber, const std::string& name)
        {
            return GetCondition(runNumber, _typesByName[name]);
        }


        virtual ~DataProvider() { }                                 // Destructor

    protected:


        DataProvider() { }

        DataProvider(const DataProvider &) = default;               // Copy constructor
        DataProvider(DataProvider &&) = default;                    // Move constructor
        DataProvider &operator=(const DataProvider &) & = default;  // Copy assignment operator
        DataProvider &operator=(DataProvider &&) & = default;       // Move assignment operator


        std::vector<ConditionType> _types;                          /// Condition types
        std::map<std::string, ConditionType> _typesByName;          /// Condition types mapped by name

    private:
        //bool mAreConditionTypesLoaded;
    };


}

#endif //RCDB_CPP_DATAPROVIDER_H

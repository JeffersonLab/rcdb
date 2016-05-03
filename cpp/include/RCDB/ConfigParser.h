//
// Created by romanov on 4/28/16.
//

#ifndef RCDB_CPP_CONFIGPARSER_H
#define RCDB_CPP_CONFIGPARSER_H

#include <string>
#include <vector>
#include <map>
#include <algorithm>

#include "StringUtils.h"

namespace rcdb
{
    class ConfigSection
    {
    public:

        std::string Name;
        std::vector<std::vector<std::string> > Rows;
        std::map<std::string, std::string> NameValues;
        std::map<std::string, std::vector<std::string>> NameVectors;
    };

    //Result of parsing the config file
    class ConfigFileParseResult
    {
    public:

        ConfigFileParseResult(std::vector<std::string> SectionNames)
        {
            for(auto sectionName: SectionNames) {
                SectionNames.push_back(sectionName);
            }
        }
        std::vector<std::string> SectionNames;
        std::map<std::string, rcdb::ConfigSection> Sections;
        std::vector<std::string> FoundSectionNames;
    };

    class ConfigParser
    {
    public:

        static ConfigFileParseResult Parse(std::string content, std::vector<std::string> awaitedSections)
        {
            auto lines = StringUtils::Split(content, "\n");

            return Parse(lines, awaitedSections);
        }


        static ConfigFileParseResult Parse(std::vector<std::string> lines, std::vector<std::string> awaitedSections)
        {
            using namespace std;
            auto result = ConfigFileParseResult(awaitedSections);
            auto currentSection = ConfigSection();
            currentSection.Name = string("");

            for(string line : lines)
            {
                //trim the line
                line.erase(line.find_last_not_of(" \n\r\t")+1);

                //Skip comments
                if (line.find("----") == 0 || line.find("====") == 0) {
                    continue;
                }

                // Split tokens by lexical rules
                std::vector<std::string> tokens = StringUtils::LexicalSplit(line, true);

                for(string& token:tokens) {
                    StringUtils::trim(token);
                }

                // Skip if there is no tokens
                if (tokens.size() == 0 || tokens[0] == "") continue;

                bool isSection = false;
                for(auto awaitedSection: awaitedSections) {
                    if(awaitedSection == tokens[0]) {
                        isSection = true;
                        break;
                    }
                }

                // Is this a section name?
                if (isSection) {
                    // Yehoooo new section! Save the old one!
                    if (currentSection.Name != "") {
                        result.Sections[currentSection.Name] = currentSection;
                    }
                    currentSection = ConfigSection();
                    currentSection.Name = tokens[0];

                    result.FoundSectionNames.push_back(tokens[0]);
                    continue;
                }



                currentSection.Rows.push_back(tokens);

                // We have a name-value pair
                if (tokens.size() == 2)
                {
                    currentSection.NameValues[tokens[0]] = tokens[1];
                }

                // We have a name-value pair
                if (tokens.size() > 2)
                {
                    vector<string> values;
                    for(size_t i=1; i<tokens.size(); i++ ){
                        values.push_back(tokens[i]);
                    }

                    currentSection.NameVectors[tokens[0]] = values;
                }

            }
            // Save the section we filled
            if (currentSection.Name != "") {
                result.Sections[currentSection.Name] = currentSection;
            }

            return result;
        }
    };
}

#endif //RCDB_CPP_CONFIGPARSER_H

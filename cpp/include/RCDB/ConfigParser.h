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

        int SlotNumber = -1;
        std::string Name;
        std::vector<std::vector<std::string> > Rows;
        std::map<std::string, std::string> NameValues;
        std::map<std::string, std::vector<std::string>> NameVectors;
    };

    class SlotSection
    {
    public:
        std::string FullLine;
        std::string Name;
        int SlotNumber;
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
        std::map<int, rcdb::ConfigSection> SectionsBySlotNumber;    /// If it is sectioned file
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

        static std::vector<rcdb::SlotSection> FindSlotSections(std::vector<std::string> lines, std::string slotSectionStart)
        {
            using namespace std;
            std::vector<rcdb::SlotSection> result;


            for(string line : lines) {
                //trim the line
                line.erase(line.find_last_not_of(" \n\r\t") + 1);

                //Skip comments
                if (line.find("#") == 0 ||line.find("----") == 0 || line.find("====") == 0) {
                    continue;
                }

                // Split tokens by lexical rules
                std::vector<std::string> tokens = StringUtils::LexicalSplit(line, true);

                for(string& token:tokens) {
                    StringUtils::trim(token);
                }

                // Skip if there is no tokens
                if (tokens.size() == 0 || tokens[0] == "") continue;

                if(slotSectionStart == tokens[0] && tokens.size()>1) {

                    SlotSection section;
                    section.FullLine = line;
                    section.Name = slotSectionStart;
                    section.SlotNumber = std::stoi(tokens[1]);
                    result.push_back(section);
                }
            }

            return result;
        }


        static ConfigFileParseResult Parse(std::vector<std::string> lines, std::vector<std::string> awaitedSections, bool sectionMayContainSpace=false)
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
                if (line.find("#") == 0 ||line.find("----") == 0 || line.find("====") == 0) {
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
                    if(awaitedSection == (sectionMayContainSpace? line:tokens[0])) {
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
                    currentSection.Name = (sectionMayContainSpace? line:tokens[0]);

                    result.FoundSectionNames.push_back(currentSection.Name);
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

        static ConfigFileParseResult ParseWithSlots(std::string content, std::string slotPrefix)
        {
            auto lines = StringUtils::Split(content, "\n");

            return ParseWithSlots(lines, slotPrefix);
        }

        static ConfigFileParseResult ParseWithSlots(std::vector<std::string> lines, std::string slotPrefix)
        {
            using namespace std;
            auto sections = FindSlotSections(lines, slotPrefix);

            vector<string> sectionNames;

            //First auto find sections
            for (uint i = 0; i < sections.size(); ++i) {
                sectionNames.push_back(sections[i].FullLine);
            }

            // Parse file the usual way
            auto result = Parse(lines, sectionNames, true);

            // Update parse result
            for (uint i = 0; i < sections.size(); ++i) {
                result.SectionsBySlotNumber[sections[i].SlotNumber] = result.Sections[sections[i].FullLine];
            }
            return result;

        }
    };
}

#endif //RCDB_CPP_CONFIGPARSER_H

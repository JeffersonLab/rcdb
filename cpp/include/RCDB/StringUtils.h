//
// Created by romanov on 4/28/16.
//

#ifndef RCDB_CPP_STRINGUTILS_H
#define RCDB_CPP_STRINGUTILS_H


#include <cstdlib>
#include <string>
#include <vector>

#include <algorithm>
#include <functional>
#include <cctype>
#include <locale>


#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>

//returns true if char is one of CCDB_BLANK_CHARACTERS
#define RCDB_CHECK_CHAR_IS_BLANK(character) ((character)==' ' || (character)=='\n' || (character)=='\t' || (character)=='\v' || (character)=='\r' || (character)=='\f')

class StringUtils {
public:

   static inline std::string GetFormattedTime(std::tm time) {
        char buff[20];
        strftime(buff, 20, "%Y-%m-%d %H:%M:%S", &time);
        return std::string(buff);
    }

    static inline std::string GetFormattedTime(std::time_t time) {
        return GetFormattedTime(*localtime(&time));
    }

    // trim from start (in place)
    static inline void ltrim(std::string &s) {
        s.erase(s.begin(), std::find_if(s.begin(), s.end(), std::not1(std::ptr_fun<int, int>(std::isspace))));
    }

    // trim from end (in place)
    static inline void rtrim(std::string &s) {
        s.erase(std::find_if(s.rbegin(), s.rend(), std::not1(std::ptr_fun<int, int>(std::isspace))).base(), s.end());
    }

    // trim from both ends (in place)
    static inline void trim(std::string &s) {
        ltrim(s);
        rtrim(s);
    }

    // trim from start (copying)
    static inline std::string ltrimmed(std::string s) {
        ltrim(s);
        return s;
    }

    // trim from end (copying)
    static inline std::string rtrimmed(std::string s) {
        rtrim(s);
        return s;
    }

    // trim from both ends (copying)
    static inline std::string trimmed(std::string s) {
        trim(s);
        return s;
    }

    static int Replace(const std::string& pattern, const std::string& replace, const std::string& source, std::string &out) {
        int matches = 0;
        out.assign(source);

        std::string::size_type start = out.find( pattern );

        // Replace all matches
        while ( start != std::string::npos ) {
            matches++;
            out.replace( start, pattern.size(), replace );
            // Be sure to jump forward by the replacement length
            start = out.find( pattern, start + replace.size() );
        }
        return matches;
    }


    static std::string Replace(const std::string& pattern, const std::string& replace, const std::string& source)
    {
        std::string out("");
        Replace(pattern, replace, source, out);
        return out;
    }


    static bool WildCardCheck( const char* pattern, const char* source )
    {
        char *cp, *mp;
        while ((*source) && (*pattern != '*')) {
            if ((*pattern != *source) && (*pattern != '?')) {
                return 0;
            }

            pattern++;
            source++;
        }

        while (*source) {
            if (*pattern == '*') {
                if (!*++pattern) {
                    return 1;
                }

                mp = const_cast<char *>(pattern);
                cp = const_cast<char *>(source+1);
            }
            else if ((*pattern == *source) || (*pattern == '?')) {
                pattern++;
                source++;
            }
            else {
                pattern = mp;
                source = cp++;
            }
        }

        while (*pattern == '*') {
            pattern++;
        }

        return !*pattern;
    }


    static std::vector<std::string> Split( const std::string &s, const std::string& delimiters /*= " "*/ )
    {
        std::vector<std::string> elements;
        return Split(s, elements, delimiters);
    }


    static std::vector<std::string> Split( const std::string& str, std::vector<std::string>& tokens, const std::string& delimiters /*= " "*/ )
    {
        // Skip delimiters at beginning.
        auto lastPos = str.find_first_not_of(delimiters, 0);

        // Find first "non-delimiter".
        auto pos     = str.find_first_of(delimiters, lastPos);

        while (std::string::npos != pos || std::string::npos != lastPos)
        {
            // Found a token, add it to the vector.
            tokens.push_back(str.substr(lastPos, pos - lastPos));
            // Skip delimiters.  Note the "not_of"
            lastPos = str.find_first_not_of(delimiters, pos);
            // Find next "non-delimiter"
            pos = str.find_first_of(delimiters, lastPos);
        }
        return tokens;
    }


    /** Splits string to lexical values.
     *
     * LexicalSplit treats:
     * 1) "quoted values" as one value,
     * 2) '#' not in the beginning of the file are treated as comments to the end of the line
     * 3) skips all white space characters. All specification is in doc/ccdb_file_format.pdf
     */
    static std::vector<std::string> LexicalSplit( const std::string& source, bool skipComments = false )
    {
        std::vector<std::string> tokens;
        LexicalSplit(tokens, source, skipComments);
        return tokens;
    }


    static void LexicalSplit( std::vector<std::string>& tokens, const std::string& source,  bool skipComments = false )
    {
        //

        /** Splits string to lexical values.
        *
        * LexicalSplit treats:
        * 1) "quoted values" as one value,
        * 2) '#' not in the beginning of the file are treated as comments to the end of the line
        * 3) skips all white space characters. All specification is in doc/ccdb_file_format.pdf
        *
        * @remark
        * Handling inconsistencies and errors while readout parse time:
        *  -  No ending quote . If no ending  is found, string value will be taken
        *     until the end of line.
        *  -  Comment inside a string. Comment symbol inside the line is ignored.
        *     So if you have a record in the file "info #4" it will be read just
        *     as "info #4" string
        *  -  Sticking string. In case of there is no spaces between symbols and
        *     an quotes, all will be merged as one string. I.e.:
        *     John" Smith" will be parsed as one value: "John Smith"
        *     John" "Smith will be parsed as one value: "John Smith"
        *     but be careful(!) not to forget to do a spaces between columns
        *     5.14"Smith" will be parsed as one value "5.14Smith" that probably would
        *     lead to errors if these were two different columns
        *  -  If data contains string fields they are taken into "..." characters. All "
        *     inside string should be saved by \" symbol. All words and symbols
        *     inside "..." will be interpreted as string entity.
        *
        */
        //clear output
        tokens.clear();
        bool stringIsStarted = false; //Indicates that we meet '"' and looking for second one
        //bool isSlash = false; //indicates if \ sign is happen to shield the quote or anothe slash
        std::string readValue="";
        //iterate through string
        for(size_t i=0; i<source.length(); i++)
        {
            if(RCDB_CHECK_CHAR_IS_BLANK(source[i]) && !stringIsStarted)
            {
                //we have a space! Is it a space that happens after value?
                if(readValue.length()>0)
                {
                    tokens.push_back(readValue);
                    readValue="";
                }
            }
            else
            {
                //it is not a blank character!
                if(source[i]=='\\' && stringIsStarted && i<(source.length()-1) && source[i+1]=='"')
                {
                    //ok! we found a \" inside a string! Not a problem! At all!

                    i++; //skip this \ symbol
                    readValue+=source[i]; //it is just one more symbol in value
                }
                else if(source[i]=='#' && !stringIsStarted) //lets check if it is a comment symbol that is not incide a string...
                {
                    //it is a comment started...
                    //lets save what we collected for now if we collected
                    if(readValue.length()>0)
                    {
                        tokens.push_back(readValue);
                        readValue="";
                    }

                    //and put there the rest of the lint(all comment) if there is something to put
                    if(i<(source.length()-1))
                    {
                        if(!skipComments) tokens.push_back(source.substr(i));

                        //after that gentlemen should exit
                        return;
                    }
                }
                else if(source[i]=='"')
                {

                    //it is a beginnig or ending  of a string
                    //just set appropriate flag and continue
                    stringIsStarted = !stringIsStarted;
                }
                else
                {
                    //it is just one more symbol in file
                    readValue+=source[i];
                }
            }

            //last we have is to check that
            //it is not the end of the lint
            if(i==(source.length()-1) && readValue.length()>0)
            {
                tokens.push_back(readValue);
                readValue="";
            }
        }
    }
};


#endif //RCDB_CPP_STRINGUTILS_H

#include <cstdlib>
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>

#include "TDB/StringUtils.h"

using namespace std;
namespace tdb
{



struct DHTMLReplace {
    string match;
    string replace;
} gHTMLReplaceCodes[] = {
    {"&", "&amp;"},
    {"<", "&lt;"}, 
    {">", "&gt;"},
    {"\"","&quot;"}
};


//_____________________________________________________________________________________________________________
int StringUtils::Replace(const string& pattern, const string& replace, const string& source, string &out)
{
    int matches = 0;
    out.assign(source);

    string::size_type start = out.find( pattern );

    // Replace all matches
    while ( start != string::npos ) {
        matches++;
        out.replace( start, pattern.size(), replace );
        // Be sure to jump forward by the replacement length
        start = out.find( pattern, start + replace.size() );
    }
    return matches;
}


//___________________________________________________________________________________________________
string StringUtils::Replace(const string& pattern, const string& replace, const string& source)
{
    string out("");
    Replace(pattern, replace, source, out);
    return out;
}

//______________________________________________________________________________
bool StringUtils::WildCardCheck( const char* pattern, const char* source )
{   
    char *cp, *mp;
    while ((*source) && (*pattern != '*')) 
    {
        if ((*pattern != *source) && (*pattern != '?')) 
        {
                return 0;
        }

        pattern++;
        source++;
    }

    while (*source) 
    {
        if (*pattern == '*') 
        {
            if (!*++pattern) 
            {
                    return 1;
            }

            mp = const_cast<char *>(pattern);
            cp = const_cast<char *>(source+1);
        } 
        else if ((*pattern == *source) || (*pattern == '?')) 
        {
            pattern++;
            source++;
        } 
        else 
        {
            pattern = mp;
            source = cp++;
        }
    }

    while (*pattern == '*') 
    {
        pattern++;
    }

    return !*pattern;
}


//___________________________________________________________________________________________________________
std::vector<std::string> StringUtils::Split( const std::string &s, const string& delimiters /*= " "*/ )
{
    std::vector<std::string> elems;
    return Split(s, elems, delimiters);
}


//________________________________________________________________________________________________________________________
vector<string> & StringUtils::Split( const string& str, vector<string>& tokens, const string& delimiters /*= " "*/ )
{
    // Skip delimiters at beginning.
    string::size_type lastPos = str.find_first_not_of(delimiters, 0);

    // Find first "non-delimiter".
    string::size_type pos     = str.find_first_of(delimiters, lastPos);

    while (string::npos != pos || string::npos != lastPos)
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


//______________________________________________________________________________
int StringUtils::ParseInt( const string& source, bool *result/*=NULL*/  )
{
    return atoi(source.c_str()); //ugly isn't it?
}


//______________________________________________________________________________
unsigned int StringUtils::ParseUInt( const string& source, bool *result/*=NULL*/  )
{
    return static_cast<unsigned int>(atoi(source.c_str())); //ugly isn't it?
}


//______________________________________________________________________________
long StringUtils::ParseLong( const string& source, bool *result/*=NULL*/  )
{
    return atol(source.c_str()); //ugly isn't it?
}


//______________________________________________________________________________
unsigned long StringUtils::ParseULong( const string& source, bool *result/*=NULL*/  )
{
    return static_cast<unsigned long>(atol(source.c_str())); //ugly isn't it?
}


//______________________________________________________________________________
bool StringUtils::ParseBool( const string& source, bool *result/*=NULL*/  )
{
    if(source=="true") return true;
    if(source=="false") return false;

    return static_cast<bool>(atoi(source.c_str())!=0); //ugly isn't it?
}

//___________________________________________________________________________________
double StringUtils::ParseDouble( const string& source, bool *result/*=NULL*/  )
{
    return atof(source.c_str()); //ugly isn't it?
}

//_______________________________________________________________________________________
std::string StringUtils::ParseString( const string& source, bool *result/*=NULL*/  )
{
    return string(source);
}


//_______________________________________________________________________________________
time_t StringUtils::ParseUnixTime( const string& source, bool *result/*=NULL*/  )
{   
    return static_cast<time_t>(ParseULong(source, result));
}


//______________________________________________________________________________
std::vector<string> StringUtils::LexicalSplit( const std::string& source )
{
    //

    /** Splits string to lexical values.
    *
    * LexicalSplit treats:
    * 1) "quoted values" as one value,
    * 2) '#' not in the beginning of the file are treated as comments to the end of the line
    * 3) skips all white space characters. All specification is in doc/ccdb_file_format.pdf
    */
    std::vector<string> tokens;
    LexicalSplit(tokens, source);
    return tokens;
}
//____________________________________________________________________________________________
void StringUtils::LexicalSplit( std::vector<string>& tokens, const std::string& source )
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
    *  ?  No ending quote . If no ending “ is found, string value will be taken
    *     until the end of line.
    *  ?  Comment inside a string. Comment symbol inside the line is ignored. 
    *     So if you have a record in the file “info #4” it will be read just
    *     as “info #4” string
    *  ?  Sticked string. In case of there is no spaces between symbols and
    *     an quotes, all will be merged as one string. I.e.:
    *     John" Smith" will be parsed as one value: "John Smith"
    *     John" "Smith will be parsed as one value: "John Smith"
    *     but be careful(!) not to forget to do a spaces between columns
    *     5.14”Smith” will be parsed as one value “5.14Smith” that probably would
    *     lead to errors if these were two different columns
    *  ?  If data contains string fields they are taken into “...” characters. All “
    *     inside string should be saved by \” symbol. All words and symbols
    *     inside “...” will be interpreted as string entity.
    *
    */
    //clear output
    tokens.clear();
    bool stringIsStarted = false; //Indicates that we meet '"' and looking for second one
    bool isSlash = false; //indicates if \ sign is happen to shield the quote or anothe slash
    std::string readValue="";
    //iterate through string
    for(size_t i=0; i<source.length(); i++)
    {
        if(CCDB_CHECK_CHAR_IS_BLANK(source[i]) && !stringIsStarted)
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
                    tokens.push_back(source.substr(i));

                    //after that gentelment should exit
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

}
#pragma once
#include <string>
#include <memory>

using namespace std;

namespace tdb
{
    class Error
    {
    public:
        
        Error() {}

        Error(const string& message): 
            _message(message) 
        { }

        Error(const string& message, const shared_ptr<Error>& innerError): 
            _message(message), 
            _innerError(innerError)
        { }

        Error(const string& message, Error* innerError): 
            _message(message), 
            _innerError(innerError)
        { }

        ~Error(void){}
        
        /** @brief Returns message that was set for this error. 
         *
         * Use @see FullMessage() to get message that includes messages from all inner errors
         *
         * @return   std::string
         */
        string Message() const { return _message; }


        /** @brief Returns message including all messages of all inner errors
         *
         * @return std::string self message + all messages of all inner errors
         */
        string FullMessage() const 
        { 
            if(InnerError())
            {
                return _message + " " + InnerError()->FullMessage(); 
            }
            else
            {
                return _message; 
            }
        }

        shared_ptr<Error> InnerError() const { return _innerError; }

    private:
        Error(const Error& err);
        string _message;
        shared_ptr<Error> _innerError;
    };
}



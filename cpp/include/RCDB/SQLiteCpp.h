
#ifndef SQLITE_CPP_HEADER_
#define SQLITE_CPP_HEADER_

#include <sqlite3.h>
#include <cassert>
#include <stdexcept>
#include <string>
#include <utility>
#include <string>
#include <map>
#include <string>
#include <limits>
#include <string>
#include <cstring>
#include <iostream>
#include <fstream>
#include <string>

class Database;
class Statement;
/**
 * @file    Assertion.h
 * @ingroup SQLiteCpp
 * @brief   Definition of the SQLITECPP_ASSERT() macro.
 *
 * Copyright (c) 2012-2016 Sebastien Rombauts (sebastien.rombauts@gmail.com)
 *
 * Distributed under the MIT License (MIT) (See accompanying file LICENSE.txt
 * or copy at http://opensource.org/licenses/MIT)
 */



/**
 * SQLITECPP_ASSERT SQLITECPP_ASSERT() is used in destructors, where exceptions shall not be thrown
 *
 * Define SQLITECPP_ENABLE_ASSERT_HANDLER at the project level
 * and define a SQLite::assertion_failed() assertion handler
 * to tell SQLiteC++ to use it instead of assert() when an assertion fail.
*/
#ifdef SQLITECPP_ENABLE_ASSERT_HANDLER

// if an assert handler is provided by user code, use it instead of assert()
namespace SQLite
{
    // declaration of the assert handler to define in user code
    void assertion_failed(const char* apFile, const long apLine, const char* apFunc,
                          const char* apExpr, const char* apMsg);

#ifdef _MSC_VER
    #define __func__ __FUNCTION__
#endif
// call the assert handler provided by user code
#define SQLITECPP_ASSERT(expression, message) \
    if (!(expression))  SQLite::assertion_failed(__FILE__, __LINE__, __func__, #expression, message)
} // namespace SQLite

#else

// if no assert handler provided by user code, use standard assert()
// (note: in release mode assert() does nothing)
#define SQLITECPP_ASSERT(expression, message)   assert(expression && message)

#endif
/**
 * @file    Exception.h
 * @ingroup SQLiteCpp
 * @brief   Encapsulation of the error message from SQLite3 on a std::runtime_error.
 *
 * Copyright (c) 2012-2016 Sebastien Rombauts (sebastien.rombauts@gmail.com)
 *
 * Distributed under the MIT License (MIT) (See accompanying file LICENSE.txt
 * or copy at http://opensource.org/licenses/MIT)
 */


// Forward declaration to avoid inclusion of <sqlite3.h> in a header
struct sqlite3;

/// Compatibility with non-clang compilers.
#ifndef __has_feature
#define __has_feature(x) 0
#endif

// Detect whether the compiler supports C++11 noexcept exception specifications.
#if (  defined(__GNUC__) && ((__GNUC__ == 4 && __GNUC_MINOR__ >= 7) || (__GNUC__ > 4)) \
    && defined(__GXX_EXPERIMENTAL_CXX0X__))
// GCC 4.7 and following have noexcept
#elif defined(__clang__) && __has_feature(cxx_noexcept)
// Clang 3.0 and above have noexcept
#elif defined(_MSC_VER) && _MSC_VER > 1800
// Visual Studio 2015 and above have noexcept
#else
    // Visual Studio 2013 does not support noexcept, and "throw()" is deprecated by C++11
    #define noexcept
#endif


namespace SQLite
{


/**
 * @brief Encapsulation of the error message from SQLite3, based on std::runtime_error.
 */
    class Exception : public std::runtime_error
    {
    public:
        /**
         * @brief Encapsulation of the error message from SQLite3, based on std::runtime_error.
         *
         * @param[in] aErrorMessage The string message describing the SQLite error
         */
        explicit Exception(const std::string& aErrorMessage);

        /**
         * @brief Encapsulation of the error message from SQLite3, based on std::runtime_error.
         *
         * @param[in] aErrorMessage The string message describing the SQLite error
         * @param[in] ret           Return value from function call that failed.
         */
        Exception(const std::string& aErrorMessage, int ret);

        /**
          * @brief Encapsulation of the error message from SQLite3, based on std::runtime_error.
          *
          * @param[in] apSQLite The SQLite object, to obtain detailed error messages from.
          */
        explicit Exception(sqlite3* apSQLite);

        /**
         * @brief Encapsulation of the error message from SQLite3, based on std::runtime_error.
         *
         * @param[in] apSQLite  The SQLite object, to obtain detailed error messages from.
         * @param[in] ret       Return value from function call that failed.
         */
        Exception(sqlite3* apSQLite, int ret);

        /// Return the result code (if any, otherwise -1).
        inline int getErrorCode() const noexcept // nothrow
        {
            return mErrcode;
        }

        /// Return the extended numeric result code (if any, otherwise -1).
        inline int getExtendedErrorCode() const noexcept // nothrow
        {
            return mExtendedErrcode;
        }

        /// Return a string, solely based on the error code
        const char* getErrorStr() const noexcept; // nothrow

    private:
        const int mErrcode;         ///< Error code value
        const int mExtendedErrcode; ///< Detailed error code if any
    };


}  // namespace SQLite
/**
 * @file    VariadicBind.h
 * @ingroup SQLiteCpp
 * @brief   Convenience function for Statement::bind(...)
 *
 * Copyright (c) 2016 Paul Dreik (github@pauldreik.se)
 * Copyright (c) 2016 Sebastien Rombauts (sebastien.rombauts@gmail.com)
 *
 * Distributed under the MIT License (MIT) (See accompanying file LICENSE.txt
 * or copy at http://opensource.org/licenses/MIT)
 */

#if (__cplusplus >= 201402L) || ( defined(_MSC_VER) && (_MSC_VER >= 1900) ) // c++14: Visual Studio 2015


/// @cond
#include <initializer_list>

namespace SQLite
{

/// implementation detail for variadic bind.
namespace detail {
template<class F, class ...Args, std::size_t ... I>
inline void invoke_with_index(F&& f, std::integer_sequence<std::size_t, I...>, const Args& ...args)
{
    std::initializer_list<int> { (f(I+1, args), 0)... };
}

/// implementation detail for variadic bind.
template<class F, class ...Args>
inline void invoke_with_index(F&& f, const Args& ... args)
{
    invoke_with_index(std::forward<F>(f), std::index_sequence_for<Args...>(), args...);
}

} // namespace detail
/// @endcond

/**
 * \brief Convenience function for calling Statement::bind(...) once for each argument given.
 *
 * This takes care of incrementing the index between each calls to bind.
 *
 * This feature requires a c++14 capable compiler.
 *
 * \code{.cpp}
 * SQLite::Statement stm("SELECT * FROM MyTable WHERE colA>? && colB=? && colC<?");
 * bind(stm,a,b,c);
 * //...is equivalent to
 * stm.bind(1,a);
 * stm.bind(2,b);
 * stm.bind(3,c);
 * \endcode
 * @param s statement
 * @param args one or more args to bind.
 */
template<class ...Args>
void bind(SQLite::Statement& s, const Args& ... args)
{
    static_assert(sizeof...(args) > 0, "please invoke bind with one or more args");

    auto f=[&s](std::size_t index, const auto& value)
    {
        s.bind(index, value);
    };
    detail::invoke_with_index(f, args...);
}

}  // namespace SQLite

#endif // c++14

/**
 * @file    Statement.h
 * @ingroup SQLiteCpp
 * @brief   A prepared SQLite Statement is a compiled SQL query ready to be executed, pointing to a row of result.
 *
 * Copyright (c) 2012-2016 Sebastien Rombauts (sebastien.rombauts@gmail.com)
 *
 * Distributed under the MIT License (MIT) (See accompanying file LICENSE.txt
 * or copy at http://opensource.org/licenses/MIT)
 */



// Forward declarations to avoid inclusion of <sqlite3.h> in a header
struct sqlite3;
struct sqlite3_stmt;


namespace SQLite
{


// Forward declaration
    class Database;
    class Column;

    extern const int OK; ///< SQLITE_OK

/**
 * @brief RAII encapsulation of a prepared SQLite Statement.
 *
 * A Statement is a compiled SQL query ready to be executed step by step
 * to provide results one row at a time.
 *
 * Resource Acquisition Is Initialization (RAII) means that the Statement
 * is compiled in the constructor and finalized in the destructor, so that there is
 * no need to worry about memory management or the validity of the underlying SQLite Statement.
 *
 * Thread-safety: a Statement object shall not be shared by multiple threads, because :
 * 1) in the SQLite "Thread Safe" mode, "SQLite can be safely used by multiple threads
 *    provided that no single database connection is used simultaneously in two or more threads."
 * 2) the SQLite "Serialized" mode is not supported by SQLiteC++,
 *    because of the way it shares the underling SQLite precompiled statement
 *    in a custom shared pointer (See the inner class "Statement::Ptr").
 */
    class Statement
    {
        friend class Column; // For access to Statement::Ptr inner class

    public:
        /**
         * @brief Compile and register the SQL query for the provided SQLite Database Connection
         *
         * @param[in] aDatabase the SQLite Database Connection
         * @param[in] apQuery   an UTF-8 encoded query string
         *
         * Exception is thrown in case of error, then the Statement object is NOT constructed.
         */
        Statement(Database& aDatabase, const char* apQuery);

        /**
         * @brief Compile and register the SQL query for the provided SQLite Database Connection
         *
         * @param[in] aDatabase the SQLite Database Connection
         * @param[in] aQuery    an UTF-8 encoded query string
         *
         * Exception is thrown in case of error, then the Statement object is NOT constructed.
         */
        Statement(Database& aDatabase, const std::string& aQuery);

        /// Finalize and unregister the SQL query from the SQLite Database Connection.
        virtual ~Statement() noexcept; // nothrow

        /// Reset the statement to make it ready for a new execution.
        void reset();

        /**
         * @brief Clears away all the bindings of a prepared statement.
         *
         *  Contrary to the intuition of many, reset() does not reset the bindings on a prepared statement.
         *  Use this routine to reset all parameters to NULL.
         */
        void clearBindings(); // throw(SQLite::Exception)

        ////////////////////////////////////////////////////////////////////////////
        // Bind a value to a parameter of the SQL statement,
        // in the form "?" (unnamed), "?NNN", ":VVV", "@VVV" or "$VVV".
        //
        // Can use the parameter index, starting from "1", to the higher NNN value,
        // or the complete parameter name "?NNN", ":VVV", "@VVV" or "$VVV"
        // (prefixed with the corresponding sign "?", ":", "@" or "$")
        //
        // Note that for text and blob values, the SQLITE_TRANSIENT flag is used,
        // which tell the sqlite library to make its own copy of the data before the bind() call returns.
        // This choice is done to prevent any common misuses, like passing a pointer to a
        // dynamic allocated and temporary variable (a std::string for instance).
        // This is under-optimized for static data (a static text define in code)
        // as well as for dynamic allocated buffer which could be transfer to sqlite
        // instead of being copied.
        // => if you know what you are doing, use bindNoCopy() instead of bind()

        /**
         * @brief Bind an int value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         */
        void bind(const int aIndex, const int           aValue);
        /**
         * @brief Bind a 32bits unsigned int value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         */
        void bind(const int aIndex, const unsigned      aValue);
        /**
         * @brief Bind a 64bits int value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         */
        void bind(const int aIndex, const long long     aValue);
        /**
         * @brief Bind a double (64bits float) value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         */
        void bind(const int aIndex, const double        aValue);
        /**
         * @brief Bind a string value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         *
         * @note Uses the SQLITE_TRANSIENT flag, making a copy of the data, for SQLite internal use
         */
        void bind(const int aIndex, const std::string&  aValue);
        /**
         * @brief Bind a text value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         *
         * @note Uses the SQLITE_TRANSIENT flag, making a copy of the data, for SQLite internal use
         */
        void bind(const int aIndex, const char*         apValue);
        /**
         * @brief Bind a binary blob value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         *
         * @note Uses the SQLITE_TRANSIENT flag, making a copy of the data, for SQLite internal use
         */
        void bind(const int aIndex, const void*         apValue, const int aSize);
        /**
         * @brief Bind a string value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1).
         *
         * The string can contain null characters as it is binded using its size.
         *
         * @warning Uses the SQLITE_STATIC flag, avoiding a copy of the data. The string must remains unchanged while executing the statement.
         */
        void bindNoCopy(const int aIndex, const std::string&    aValue);
        /**
         * @brief Bind a text value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         *
         * Main usage is with null-terminated literal text (aka in code static strings)
         *
         * @warning Uses the SQLITE_STATIC flag, avoiding a copy of the data. The string must remains unchanged while executing the statement.
         */
        void bindNoCopy(const int aIndex, const char*           apValue);
        /**
         * @brief Bind a binary blob value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         *
         * @warning Uses the SQLITE_STATIC flag, avoiding a copy of the data. The string must remains unchanged while executing the statement.
         */
        void bindNoCopy(const int aIndex, const void*           apValue, const int aSize);
        /**
         * @brief Bind a NULL value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         *
         * @see clearBindings() to set all bound parameters to NULL.
         */
        void bind(const int aIndex);

        /**
         * @brief Bind an int value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         */
        void bind(const char* apName, const int             aValue);
        /**
         * @brief Bind a 32bits unsigned int value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         */
        void bind(const char* apName, const unsigned        aValue);
        /**
         * @brief Bind a 64bits int value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         */
        void bind(const char* apName, const long long       aValue);
        /**
         * @brief Bind a double (64bits float) value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         */
        void bind(const char* apName, const double          aValue);
        /**
         * @brief Bind a string value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         *
         * @note Uses the SQLITE_TRANSIENT flag, making a copy of the data, for SQLite internal use
         */
        void bind(const char* apName, const std::string&    aValue);
        /**
         * @brief Bind a text value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         *
         * @note Uses the SQLITE_TRANSIENT flag, making a copy of the data, for SQLite internal use
         */
        void bind(const char* apName, const char*           apValue);
        /**
         * @brief Bind a binary blob value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         *
         * @note Uses the SQLITE_TRANSIENT flag, making a copy of the data, for SQLite internal use
         */
        void bind(const char* apName, const void*           apValue, const int aSize);
        /**
         * @brief Bind a string value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         *
         * The string can contain null characters as it is binded using its size.
         *
         * @warning Uses the SQLITE_STATIC flag, avoiding a copy of the data. The string must remains unchanged while executing the statement.
         */
        void bindNoCopy(const char* apName, const std::string&  aValue);
        /**
         * @brief Bind a text value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         *
         * Main usage is with null-terminated literal text (aka in code static strings)
         *
         * @warning Uses the SQLITE_STATIC flag, avoiding a copy of the data. The string must remains unchanged while executing the statement.
         */
        void bindNoCopy(const char* apName, const char*         apValue);
        /**
         * @brief Bind a binary blob value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         *
         * @warning Uses the SQLITE_STATIC flag, avoiding a copy of the data. The string must remains unchanged while executing the statement.
         */
        void bindNoCopy(const char* apName, const void*         apValue, const int aSize);
        /**
         * @brief Bind a NULL value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         *
         * @see clearBindings() to set all bound parameters to NULL.
         */
        void bind(const char* apName); // bind NULL value


        /**
         * @brief Bind an int value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         */
        inline void bind(const std::string& aName, const int            aValue)
        {
            bind(aName.c_str(), aValue);
        }
        /**
         * @brief Bind a 32bits unsigned int value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         */
        inline void bind(const std::string& aName, const unsigned       aValue)
        {
            bind(aName.c_str(), aValue);
        }
        /**
         * @brief Bind a 64bits int value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         */
        inline void bind(const std::string& aName, const long long      aValue)
        {
            bind(aName.c_str(), aValue);
        }
        /**
         * @brief Bind a double (64bits float) value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         */
        inline void bind(const std::string& aName, const double         aValue)
        {
            bind(aName.c_str(), aValue);
        }
        /**
         * @brief Bind a string value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         *
         * @note Uses the SQLITE_TRANSIENT flag, making a copy of the data, for SQLite internal use
         */
        inline void bind(const std::string& aName, const std::string&    aValue)
        {
            bind(aName.c_str(), aValue);
        }
        /**
         * @brief Bind a text value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         *
         * @note Uses the SQLITE_TRANSIENT flag, making a copy of the data, for SQLite internal use
         */
        inline void bind(const std::string& aName, const char*           apValue)
        {
            bind(aName.c_str(), apValue);
        }
        /**
         * @brief Bind a binary blob value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         *
         * @note Uses the SQLITE_TRANSIENT flag, making a copy of the data, for SQLite internal use
         */
        inline void bind(const std::string& aName, const void*           apValue, const int aSize)
        {
            bind(aName.c_str(), apValue, aSize);
        }
        /**
         * @brief Bind a string value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         *
         * The string can contain null characters as it is binded using its size.
         *
         * @warning Uses the SQLITE_STATIC flag, avoiding a copy of the data. The string must remains unchanged while executing the statement.
         */
        inline void bindNoCopy(const std::string& aName, const std::string& aValue)
        {
            bindNoCopy(aName.c_str(), aValue);
        }
        /**
         * @brief Bind a text value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         *
         * Main usage is with null-terminated literal text (aka in code static strings)
         *
         * @warning Uses the SQLITE_STATIC flag, avoiding a copy of the data. The string must remains unchanged while executing the statement.
         */
        inline void bindNoCopy(const std::string& aName, const char*        apValue)
        {
            bindNoCopy(aName.c_str(), apValue);
        }
        /**
         * @brief Bind a binary blob value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         *
         * @warning Uses the SQLITE_STATIC flag, avoiding a copy of the data. The string must remains unchanged while executing the statement.
         */
        inline void bindNoCopy(const std::string& aName, const void*        apValue, const int aSize)
        {
            bindNoCopy(aName.c_str(), apValue, aSize);
        }
        /**
         * @brief Bind a NULL value to a named parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement (aIndex >= 1)
         *
         * @see clearBindings() to set all bound parameters to NULL.
         */
        inline void bind(const std::string& aName) // bind NULL value
        {
            bind(aName.c_str());
        }

        ////////////////////////////////////////////////////////////////////////////

        /**
         * @brief Execute a step of the prepared query to fetch one row of results.
         *
         *  While true is returned, a row of results is available, and can be accessed
         * thru the getColumn() method
         *
         * @see exec() execute a one-step prepared statement with no expected result
         * @see Database::exec() is a shortcut to execute one or multiple statements without results
         *
         * @return - true  (SQLITE_ROW)  if there is another row ready : you can call getColumn(N) to get it
         *                               then you have to call executeStep() again to fetch more rows until the query is finished
         *         - false (SQLITE_DONE) if the query has finished executing : there is no (more) row of result
         *                               (case of a query with no result, or after N rows fetched successfully)
         *
         * @throw SQLite::Exception in case of error
         */
        bool executeStep();

        /**
         * @brief Execute a one-step query with no expected result.
         *
         *  This method is useful for any kind of statements other than the Data Query Language (DQL) "SELECT" :
         *  - Data Definition Language (DDL) statements "CREATE", "ALTER" and "DROP"
         *  - Data Manipulation Language (DML) statements "INSERT", "UPDATE" and "DELETE"
         *  - Data Control Language (DCL) statements "GRANT", "REVOKE", "COMMIT" and "ROLLBACK"
         *
         * It is similar to Database::exec(), but using a precompiled statement, it adds :
         * - the ability to bind() arguments to it (best way to insert data),
         * - reusing it allows for better performances (efficient for multiple insertion).
         *
         * @see executeStep() execute a step of the prepared query to fetch one row of results
         * @see Database::exec() is a shortcut to execute one or multiple statements without results
         *
         * @return number of row modified by this SQL statement (INSERT, UPDATE or DELETE)
         *
         * @throw SQLite::Exception in case of error, or if row of results are returned !
         */
        int exec();

        ////////////////////////////////////////////////////////////////////////////

        /**
         * @brief Return a copy of the column data specified by its index
         *
         *  Can be used to access the data of the current row of result when applicable,
         * while the executeStep() method returns true.
         *
         *  Throw an exception if there is no row to return a Column from:
         * - if provided index is out of bound
         * - before any executeStep() call
         * - after the last executeStep() returned false
         * - after a reset() call
         *
         *  Throw an exception if the specified index is out of the [0, getColumnCount()) range.
         *
         * @param[in] aIndex    Index of the column, starting at 0
         *
         * @note    This method is not const, reflecting the fact that the returned Column object will
         *          share the ownership of the underlying sqlite3_stmt.
         *
         * @warning The resulting Column object must not be memorized "as-is".
         *          Is is only a wrapper around the current result row, so it is only valid
         *          while the row from the Statement remains valid, that is only until next executeStep() call.
         *          Thus, you should instead extract immediately its data (getInt(), getText()...)
         *          and use or copy this data for any later usage.
         */
        Column  getColumn(const int aIndex);

        /**
         * @brief Return a copy of the column data specified by its column name (less efficient than using an index)
         *
         *  Can be used to access the data of the current row of result when applicable,
         * while the executeStep() method returns true.
         *
         *  Throw an exception if there is no row to return a Column from :
         * - if provided name is not one of the aliased column names
         * - before any executeStep() call
         * - after the last executeStep() returned false
         * - after a reset() call
         *
         *  Throw an exception if the specified name is not an on of the aliased name of the columns in the result.
         *
         * @param[in] apName   Aliased name of the column, that is, the named specified in the query (not the original name)
         *
         * @note    Uses a map of column names to indexes, build on first call.
         *
         * @note    This method is not const, reflecting the fact that the returned Column object will
         *          share the ownership of the underlying sqlite3_stmt.
         *
         * @warning The resulting Column object must not be memorized "as-is".
         *          Is is only a wrapper around the current result row, so it is only valid
         *          while the row from the Statement remains valid, that is only until next executeStep() call.
         *          Thus, you should instead extract immediately its data (getInt(), getText()...)
         *          and use or copy this data for any later usage.
         *
         *  Throw an exception if the specified name is not one of the aliased name of the columns in the result.
         */
        Column  getColumn(const char* apName);

#if __cplusplus >= 201402L || (defined(_MSC_VER) && _MSC_VER >= 1900)
        /**
     * @brief Return an instance of T constructed from copies of the first N columns
     *
     *  Can be used to access the data of the current row of result when applicable,
     * while the executeStep() method returns true.
     *
     *  Throw an exception if there is no row to return a Column from:
     * - if provided column count is out of bound
     * - before any executeStep() call
     * - after the last executeStep() returned false
     * - after a reset() call
     *
     *  Throw an exception if the specified column count is out of the [0, getColumnCount()) range.
     *
     * @tparam  T   Object type to construct
     * @tparam  N   Number of columns
     *
     * @note Requires std=C++14
     */
    template<typename T, int N>
    T       getColumns();

private:
    /**
    * @brief Helper function used by getColumns<typename T, int N> to expand an integer_sequence used to generate
    *        the required Column objects
    */
    template<typename T, const int... Is>
    T       getColumns(const std::integer_sequence<int, Is...>);

public:
#endif

        /**
         * @brief Test if the column value is NULL
         *
         * @param[in] aIndex    Index of the column, starting at 0
         *
         * @return true if the column value is NULL
         *
         *  Throw an exception if the specified index is out of the [0, getColumnCount()) range.
         */
        bool    isColumnNull(const int aIndex) const;

        /**
         * @brief Test if the column value is NULL
         *
         * @param[in] apName    Aliased name of the column, that is, the named specified in the query (not the original name)
         *
         * @return true if the column value is NULL
         *
         *  Throw an exception if the specified name is not one of the aliased name of the columns in the result.
         */
        bool    isColumnNull(const char* apName) const;

        /**
         * @brief Return a pointer to the named assigned to the specified result column (potentially aliased)
         *
         * @param[in] aIndex    Index of the column in the range [0, getColumnCount()).
         *
         * @see getColumnOriginName() to get original column name (not aliased)
         *
         *  Throw an exception if the specified index is out of the [0, getColumnCount()) range.
         */
        const char* getColumnName(const int aIndex) const;

#ifdef SQLITE_ENABLE_COLUMN_METADATA
        /**
     * @brief Return a pointer to the table column name that is the origin of the specified result column
     *
     *  Require definition of the SQLITE_ENABLE_COLUMN_METADATA preprocessor macro :
     * - when building the SQLite library itself (which is the case for the Debian libsqlite3 binary for instance),
     * - and also when compiling this wrapper.
     *
     *  Throw an exception if the specified index is out of the [0, getColumnCount()) range.
     */
    const char* getColumnOriginName(const int aIndex) const;
#endif

        /**
         * @brief Return the index of the specified (potentially aliased) column name
         *
         * @param[in] apName    Aliased name of the column, that is, the named specified in the query (not the original name)
         *
         * @note Uses a map of column names to indexes, build on first call.
         *
         *  Throw an exception if the specified name is not known.
         */
        int getColumnIndex(const char* apName) const;

        ////////////////////////////////////////////////////////////////////////////

        /// Return the UTF-8 SQL Query.
        inline const std::string& getQuery() const
        {
            return mQuery;
        }
        /// Return the number of columns in the result set returned by the prepared statement
        inline int getColumnCount() const
        {
            return mColumnCount;
        }
        /// true when a row has been fetched with executeStep()
        inline bool isOk() const
        {
            return mbOk;
        }
        /// true when the last executeStep() had no more row to fetch
        inline bool isDone() const
        {
            return mbDone;
        }

        /// Return the numeric result code for the most recent failed API call (if any).
        int getErrorCode() const noexcept; // nothrow
        /// Return the extended numeric result code for the most recent failed API call (if any).
        int getExtendedErrorCode() const noexcept; // nothrow
        /// Return UTF-8 encoded English language explanation of the most recent failed API call (if any).
        const char* getErrorMsg() const noexcept; // nothrow

    private:
        /**
         * @brief Shared pointer to the sqlite3_stmt SQLite Statement Object.
         *
         * Manage the finalization of the sqlite3_stmt with a reference counter.
         *
         * This is a internal class, not part of the API (hence full documentation is in the cpp).
         */
        class Ptr
        {
        public:
            // Prepare the statement and initialize its reference counter
            Ptr(sqlite3* apSQLite, std::string& aQuery);
            // Copy constructor increments the ref counter
            Ptr(const Ptr& aPtr);
            // Decrement the ref counter and finalize the sqlite3_stmt when it reaches 0
            ~Ptr() noexcept; // nothrow (no virtual destructor needed here)

            /// Inline cast operator returning the pointer to SQLite Database Connection Handle
            inline operator sqlite3*() const
            {
                return mpSQLite;
            }

            /// Inline cast operator returning the pointer to SQLite Statement Object
            inline operator sqlite3_stmt*() const
            {
                return mpStmt;
            }

        private:
            /// @{ Unused/forbidden copy/assignment operator
            Ptr& operator=(const Ptr& aPtr);
            /// @}

        private:
            sqlite3*        mpSQLite;    //!< Pointer to SQLite Database Connection Handle
            sqlite3_stmt*   mpStmt;      //!< Pointer to SQLite Statement Object
            unsigned int*   mpRefCount;  //!< Pointer to the heap allocated reference counter of the sqlite3_stmt
            //!< (to share it with Column objects)
        };

    private:
        /// @{ Statement must be non-copyable
        Statement(const Statement&);
        Statement& operator=(const Statement&);
        /// @}

        /**
         * @brief Check if a return code equals SQLITE_OK, else throw a SQLite::Exception with the SQLite error message
         *
         * @param[in] aRet SQLite return code to test against the SQLITE_OK expected value
         */
        inline void check(const int aRet) const
        {
            if (SQLite::OK != aRet)
            {
                throw SQLite::Exception(mStmtPtr, aRet);
            }
        }

        /**
         * @brief Check if there is a row of result returnes by executeStep(), else throw a SQLite::Exception.
         */
        inline void checkRow() const
        {
            if (false == mbOk)
            {
                throw SQLite::Exception("No row to get a column from. executeStep() was not called, or returned false.");
            }
        }

        /**
         * @brief Check if there is a Column index is in the range of columns in the result.
         */
        inline void checkIndex(const int aIndex) const
        {
            if ((aIndex < 0) || (aIndex >= mColumnCount))
            {
                throw SQLite::Exception("Column index out of range.");
            }
        }

    private:
        /// Map of columns index by name (mutable so getColumnIndex can be const)
        typedef std::map<std::string, int> TColumnNames;

    private:
        std::string             mQuery;         //!< UTF-8 SQL Query
        Ptr                     mStmtPtr;       //!< Shared Pointer to the prepared SQLite Statement Object
        int                     mColumnCount;   //!< Number of columns in the result of the prepared statement
        mutable TColumnNames    mColumnNames;   //!< Map of columns index by name (mutable so getColumnIndex can be const)
        bool                    mbOk;           //!< true when a row has been fetched with executeStep()
        bool                    mbDone;         //!< true when the last executeStep() had no more row to fetch
    };


}  // namespace SQLite
/**
 * @file    Column.h
 * @ingroup SQLiteCpp
 * @brief   Encapsulation of a Column in a row of the result pointed by the prepared SQLite::Statement.
 *
 * Copyright (c) 2012-2016 Sebastien Rombauts (sebastien.rombauts@gmail.com)
 *
 * Distributed under the MIT License (MIT) (See accompanying file LICENSE.txt
 * or copy at http://opensource.org/licenses/MIT)
 */




namespace SQLite
{

    extern const int INTEGER;   ///< SQLITE_INTEGER
    extern const int FLOAT;     ///< SQLITE_FLOAT
    extern const int TEXT;      ///< SQLITE_TEXT
    extern const int BLOB;      ///< SQLITE_BLOB
    extern const int Null;      ///< SQLITE_NULL


/**
 * @brief Encapsulation of a Column in a row of the result pointed by the prepared Statement.
 *
 *  A Column is a particular field of SQLite data in the current row of result
 * of the Statement : it points to a single cell.
 *
 * Its value can be expressed as a text, and, when applicable, as a numeric
 * (integer or floating point) or a binary blob.
 *
 * Thread-safety: a Column object shall not be shared by multiple threads, because :
 * 1) in the SQLite "Thread Safe" mode, "SQLite can be safely used by multiple threads
 *    provided that no single database connection is used simultaneously in two or more threads."
 * 2) the SQLite "Serialized" mode is not supported by SQLiteC++,
 *    because of the way it shares the underling SQLite precompiled statement
 *    in a custom shared pointer (See the inner class "Statement::Ptr").
 */
    class Column
    {
    public:
        /**
         * @brief Encapsulation of a Column in a Row of the result.
         *
         * @param[in] aStmtPtr  Shared pointer to the prepared SQLite Statement Object.
         * @param[in] aIndex    Index of the column in the row of result, starting at 0
         */
        Column(Statement::Ptr& aStmtPtr, int aIndex)    noexcept; // nothrow
        /// Simple destructor
        virtual ~Column()                               noexcept; // nothrow

        // default copy constructor and assignment operator are perfectly suited :
        // they copy the Statement::Ptr which in turn increments the reference counter.

        /// Make clang happy by explicitly implementing the copy-constructor:
        Column(const Column & aOther) :
                mStmtPtr(aOther.mStmtPtr),
                mIndex(aOther.mIndex)
        {
        }

        /**
         * @brief Return a pointer to the named assigned to this result column (potentially aliased)
         *
         * @see getOriginName() to get original column name (not aliased)
         */
        const char* getName() const noexcept; // nothrow

#ifdef SQLITE_ENABLE_COLUMN_METADATA
        /**
     * @brief Return a pointer to the table column name that is the origin of this result column
     * 
     *  Require definition of the SQLITE_ENABLE_COLUMN_METADATA preprocessor macro :
     * - when building the SQLite library itself (which is the case for the Debian libsqlite3 binary for instance),
     * - and also when compiling this wrapper.
     */
    const char* getOriginName() const noexcept; // nothrow
#endif

        /// Return the integer value of the column.
        int         getInt() const noexcept; // nothrow
        /// Return the 32bits unsigned integer value of the column (note that SQLite3 does not support unsigned 64bits).
        unsigned    getUInt() const noexcept; // nothrow
        /// Return the 64bits integer value of the column (note that SQLite3 does not support unsigned 64bits).
        long long   getInt64() const noexcept; // nothrow
        /// Return the double (64bits float) value of the column
        double      getDouble() const noexcept; // nothrow
        /**
         * @brief Return a pointer to the text value (NULL terminated string) of the column.
         *
         * @warning The value pointed at is only valid while the statement is valid (ie. not finalized),
         *          thus you must copy it before using it beyond its scope (to a std::string for instance).
         */
        const char* getText(const char* apDefaultValue = "") const noexcept; // nothrow
        /**
         * @brief Return a pointer to the binary blob value of the column.
         *
         * @warning The value pointed at is only valid while the statement is valid (ie. not finalized),
         *          thus you must copy it before using it beyond its scope (to a std::string for instance).
         */
        const void* getBlob() const noexcept; // nothrow
        /**
         * @brief Return a std::string for a TEXT or BLOB column.
         *
         * Note this correctly handles strings that contain null bytes.
         */
        std::string getString() const noexcept; // nothrow

        /**
         * @brief Return the type of the value of the column
         *
         * Return either SQLite::INTEGER, SQLite::FLOAT, SQLite::TEXT, SQLite::BLOB, or SQLite::Null.
         *
         * @warning After a type conversion (by a call to a getXxx on a Column of a Yyy type),
         *          the value returned by sqlite3_column_type() is undefined.
         */
        int getType() const noexcept; // nothrow

        /// Test if the column is an integer type value (meaningful only before any conversion)
        inline bool isInteger() const noexcept // nothrow
        {
            return (SQLite::INTEGER == getType());
        }
        /// Test if the column is a floating point type value (meaningful only before any conversion)
        inline bool isFloat() const noexcept // nothrow
        {
            return (SQLite::FLOAT == getType());
        }
        /// Test if the column is a text type value (meaningful only before any conversion)
        inline bool isText() const noexcept // nothrow
        {
            return (SQLite::TEXT == getType());
        }
        /// Test if the column is a binary blob type value (meaningful only before any conversion)
        inline bool isBlob() const noexcept // nothrow
        {
            return (SQLite::BLOB == getType());
        }
        /// Test if the column is NULL (meaningful only before any conversion)
        inline bool isNull() const noexcept // nothrow
        {
            return (SQLite::Null == getType());
        }

        /**
         * @brief Return the number of bytes used by the text (or blob) value of the column
         *
         * Return either :
         * - size in bytes (not in characters) of the string returned by getText() without the '\0' terminator
         * - size in bytes of the string representation of the numerical value (integer or double)
         * - size in bytes of the binary blob returned by getBlob()
         * - 0 for a NULL value
         */
        int getBytes() const noexcept;

        /// Alias returning the number of bytes used by the text (or blob) value of the column
        inline int size() const noexcept
        {
            return getBytes ();
        }

        /// Inline cast operator to int
        inline operator int() const
        {
            return getInt();
        }
        /// Inline cast operator to 32bits unsigned integer
        inline operator unsigned int() const
        {
            return getUInt();
        }
#if (LONG_MAX == INT_MAX) // sizeof(long)==4 means the data model of the system is ILP32 (32bits OS or Windows 64bits)
        /// Inline cast operator to 32bits long
    inline operator long() const
    {
        return getInt();
    }
    /// Inline cast operator to 32bits unsigned long
    inline operator unsigned long() const
    {
        return getUInt();
    }
#else
        /// Inline cast operator to 64bits long when the data model of the system is ILP64 (Linux 64 bits...)
        inline operator long() const
        {
            return getInt64();
        }
#endif

        /// Inline cast operator to 64bits integer
        inline operator long long() const
        {
            return getInt64();
        }
        /// Inline cast operator to double
        inline operator double() const
        {
            return getDouble();
        }
        /**
         * @brief Inline cast operator to char*
         *
         * @see getText
         */
        inline operator const char*() const
        {
            return getText();
        }
        /**
         * @brief Inline cast operator to void*
         *
         * @see getBlob
         */
        inline operator const void*() const
        {
            return getBlob();
        }

#if !(defined(_MSC_VER) && _MSC_VER < 1900)
        // NOTE : the following is required by GCC and Clang to cast a Column result in a std::string
        // (error: conversion from ‘SQLite::Column’ to non-scalar type ‘std::string {aka std::basic_string<char>}’)
        // but is not working under Microsoft Visual Studio 2010, 2012 and 2013
        // (error C2440: 'initializing' : cannot convert from 'SQLite::Column' to 'std::basic_string<_Elem,_Traits,_Ax>'
        //  [...] constructor overload resolution was ambiguous)
        /**
         * @brief Inline cast operator to std::string
         *
         * Handles BLOB or TEXT, which may contain null bytes within
         *
         * @see getString
         */
        inline operator std::string() const
        {
            return getString();
        }
#endif

    private:
        Statement::Ptr  mStmtPtr;   ///< Shared Pointer to the prepared SQLite Statement Object
        int             mIndex;     ///< Index of the column in the row of result, starting at 0
    };

/**
 * @brief Standard std::ostream text inserter
 *
 * Insert the text value of the Column object, using getText(), into the provided stream.
 *
 * @param[in] aStream   Stream to use
 * @param[in] aColumn   Column object to insert into the provided stream
 *
 * @return  Reference to the stream used
 */
    std::ostream& operator<<(std::ostream& aStream, const Column& aColumn);

#if __cplusplus >= 201402L || (defined(_MSC_VER) && _MSC_VER >= 1900)

    // Create an instance of T from the first N columns, see declaration in Statement.h for full details
template<typename T, int N>
T Statement::getColumns()
{
    checkRow();
    checkIndex(N - 1);
    return getColumns<T>(std::make_integer_sequence<int, N>{});
}

// Helper function called by getColums<typename T, int N>
template<typename T, const int... Is>
T Statement::getColumns(const std::integer_sequence<int, Is...>)
{
    return T{Column(mStmtPtr, Is)...};
}

#endif

}  // namespace SQLite
/**
 * @file    Database.h
 * @ingroup SQLiteCpp
 * @brief   Management of a SQLite Database Connection.
 *
 * Copyright (c) 2012-2016 Sebastien Rombauts (sebastien.rombauts@gmail.com)
 *
 * Distributed under the MIT License (MIT) (See accompanying file LICENSE.txt
 * or copy at http://opensource.org/licenses/MIT)
 */



// Forward declarations to avoid inclusion of <sqlite3.h> in a header
//struct sqlite3;
//struct sqlite3_context;

//#ifndef SQLITE_USE_LEGACY_STRUCT // Since SQLITE 3.19 (used by default since SQLiteCpp 2.1.0)
//typedef struct sqlite3_value sqlite3_value;
//#else // Before SQLite 3.19 (legacy struct forward declaration can be activated with CMake SQLITECPP_LEGACY_STRUCT var)
//struct Mem;
//typedef struct Mem sqlite3_value;
//#endif


namespace SQLite
{

// Those public constants enable most usages of SQLiteCpp without including <sqlite3.h> in the client application.

/// The database is opened in read-only mode. If the database does not already exist, an error is returned.
    extern const int OPEN_READONLY;     // SQLITE_OPEN_READONLY
/// The database is opened for reading and writing if possible, or reading only if the file is write protected
/// by the operating system. In either case the database must already exist, otherwise an error is returned.
    extern const int OPEN_READWRITE;    // SQLITE_OPEN_READWRITE
/// With OPEN_READWRITE: The database is opened for reading and writing, and is created if it does not already exist.
    extern const int OPEN_CREATE;       // SQLITE_OPEN_CREATE

/// Enable URI filename interpretation, parsed according to RFC 3986 (ex. "file:data.db?mode=ro&cache=private")
    extern const int OPEN_URI;          // SQLITE_OPEN_URI

    extern const int OK;                ///< SQLITE_OK (used by inline check() bellow)

    extern const char*  VERSION;        ///< SQLITE_VERSION string from the sqlite3.h used at compile time
    extern const int    VERSION_NUMBER; ///< SQLITE_VERSION_NUMBER from the sqlite3.h used at compile time

/// Return SQLite version string using runtime call to the compiled library
    const char* getLibVersion() noexcept; // nothrow
/// Return SQLite version number using runtime call to the compiled library
    int   getLibVersionNumber() noexcept; // nothrow


/**
 * @brief RAII management of a SQLite Database Connection.
 *
 * A Database object manage a list of all SQLite Statements associated with the
 * underlying SQLite 3 database connection.
 *
 * Resource Acquisition Is Initialization (RAII) means that the Database Connection
 * is opened in the constructor and closed in the destructor, so that there is
 * no need to worry about memory management or the validity of the underlying SQLite Connection.
 *
 * Thread-safety: a Database object shall not be shared by multiple threads, because :
 * 1) in the SQLite "Thread Safe" mode, "SQLite can be safely used by multiple threads
 *    provided that no single database connection is used simultaneously in two or more threads."
 * 2) the SQLite "Serialized" mode is not supported by SQLiteC++,
 *    because of the way it shares the underling SQLite precompiled statement
 *    in a custom shared pointer (See the inner class "Statement::Ptr").
 */
    class Database
    {
        friend class Statement; // Give Statement constructor access to the mpSQLite Connection Handle

    public:
        /**
         * @brief Open the provided database UTF-8 filename.
         *
         * Uses sqlite3_open_v2() with readonly default flag, which is the opposite behavior
         * of the old sqlite3_open() function (READWRITE+CREATE).
         * This makes sense if you want to use it on a readonly filesystem
         * or to prevent creation of a void file when a required file is missing.
         *
         * Exception is thrown in case of error, then the Database object is NOT constructed.
         *
         * @param[in] apFilename        UTF-8 path/uri to the database file ("filename" sqlite3 parameter)
         * @param[in] aFlags            SQLite::OPEN_READONLY/SQLite::OPEN_READWRITE/SQLite::OPEN_CREATE...
         * @param[in] aBusyTimeoutMs    Amount of milliseconds to wait before returning SQLITE_BUSY (see setBusyTimeout())
         * @param[in] apVfs             UTF-8 name of custom VFS to use, or nullptr for sqlite3 default
         *
         * @throw SQLite::Exception in case of error
         */
        Database(const char* apFilename,
                 const int   aFlags         = SQLite::OPEN_READONLY,
                 const int   aBusyTimeoutMs = 0,
                 const char* apVfs          = NULL);

        /**
         * @brief Open the provided database UTF-8 filename.
         *
         * Uses sqlite3_open_v2() with readonly default flag, which is the opposite behavior
         * of the old sqlite3_open() function (READWRITE+CREATE).
         * This makes sense if you want to use it on a readonly filesystem
         * or to prevent creation of a void file when a required file is missing.
         *
         * Exception is thrown in case of error, then the Database object is NOT constructed.
         *
         * @param[in] aFilename         UTF-8 path/uri to the database file ("filename" sqlite3 parameter)
         * @param[in] aFlags            SQLite::OPEN_READONLY/SQLite::OPEN_READWRITE/SQLite::OPEN_CREATE...
         * @param[in] aBusyTimeoutMs    Amount of milliseconds to wait before returning SQLITE_BUSY (see setBusyTimeout())
         * @param[in] aVfs              UTF-8 name of custom VFS to use, or empty string for sqlite3 default
         *
         * @throw SQLite::Exception in case of error
         */
        Database(const std::string& aFilename,
                 const int          aFlags          = SQLite::OPEN_READONLY,
                 const int          aBusyTimeoutMs  = 0,
                 const std::string& aVfs            = "");

        /**
         * @brief Close the SQLite database connection.
         *
         * All SQLite statements must have been finalized before,
         * so all Statement objects must have been unregistered.
         *
         * @warning assert in case of error
         */
        virtual ~Database() noexcept; // nothrow

        /**
         * @brief Set a busy handler that sleeps for a specified amount of time when a table is locked.
         *
         *  This is useful in multithreaded program to handle case where a table is locked for writing by a thread.
         * Any other thread cannot access the table and will receive a SQLITE_BUSY error:
         * setting a timeout will wait and retry up to the time specified before returning this SQLITE_BUSY error.
         *  Reading the value of timeout for current connection can be done with SQL query "PRAGMA busy_timeout;".
         *  Default busy timeout is 0ms.
         *
         * @param[in] aBusyTimeoutMs    Amount of milliseconds to wait before returning SQLITE_BUSY
         *
         * @throw SQLite::Exception in case of error
         */
        void setBusyTimeout(const int aBusyTimeoutMs) noexcept; // nothrow

        /**
         * @brief Shortcut to execute one or multiple statements without results.
         *
         *  This is useful for any kind of statements other than the Data Query Language (DQL) "SELECT" :
         *  - Data Manipulation Language (DML) statements "INSERT", "UPDATE" and "DELETE"
         *  - Data Definition Language (DDL) statements "CREATE", "ALTER" and "DROP"
         *  - Data Control Language (DCL) statements "GRANT", "REVOKE", "COMMIT" and "ROLLBACK"
         *
         * @see Statement::exec() to handle precompiled statements (for better performances) without results
         * @see Statement::executeStep() to handle "SELECT" queries with results
         *
         * @param[in] apQueries  one or multiple UTF-8 encoded, semicolon-separate SQL statements
         *
         * @return number of rows modified by the *last* INSERT, UPDATE or DELETE statement (beware of multiple statements)
         * @warning undefined for CREATE or DROP table: returns the value of a previous INSERT, UPDATE or DELETE statement.
         *
         * @throw SQLite::Exception in case of error
         */
        int exec(const char* apQueries);

        /**
         * @brief Shortcut to execute one or multiple statements without results.
         *
         *  This is useful for any kind of statements other than the Data Query Language (DQL) "SELECT" :
         *  - Data Manipulation Language (DML) statements "INSERT", "UPDATE" and "DELETE"
         *  - Data Definition Language (DDL) statements "CREATE", "ALTER" and "DROP"
         *  - Data Control Language (DCL) statements "GRANT", "REVOKE", "COMMIT" and "ROLLBACK"
         *
         * @see Statement::exec() to handle precompiled statements (for better performances) without results
         * @see Statement::executeStep() to handle "SELECT" queries with results
         *
         * @param[in] aQueries  one or multiple UTF-8 encoded, semicolon-separate SQL statements
         *
         * @return number of rows modified by the *last* INSERT, UPDATE or DELETE statement (beware of multiple statements)
         * @warning undefined for CREATE or DROP table: returns the value of a previous INSERT, UPDATE or DELETE statement.
         *
         * @throw SQLite::Exception in case of error
         */
        inline int exec(const std::string& aQueries)
        {
            return exec(aQueries.c_str());
        }

        /**
         * @brief Shortcut to execute a one step query and fetch the first column of the result.
         *
         *  This is a shortcut to execute a simple statement with a single result.
         * This should be used only for non reusable queries (else you should use a Statement with bind()).
         * This should be used only for queries with expected results (else an exception is fired).
         *
         * @warning WARNING: Be very careful with this dangerous method: you have to
         *          make a COPY OF THE result, else it will be destroy before the next line
         *          (when the underlying temporary Statement and Column objects are destroyed)
         *
         * @see also Statement class for handling queries with multiple results
         *
         * @param[in] apQuery  an UTF-8 encoded SQL query
         *
         * @return a temporary Column object with the first column of result.
         *
         * @throw SQLite::Exception in case of error
         */
        Column execAndGet(const char* apQuery);

        /**
         * @brief Shortcut to execute a one step query and fetch the first column of the result.
         *
         *  This is a shortcut to execute a simple statement with a single result.
         * This should be used only for non reusable queries (else you should use a Statement with bind()).
         * This should be used only for queries with expected results (else an exception is fired).
         *
         * @warning WARNING: Be very careful with this dangerous method: you have to
         *          make a COPY OF THE result, else it will be destroy before the next line
         *          (when the underlying temporary Statement and Column objects are destroyed)
         *
         * @see also Statement class for handling queries with multiple results
         *
         * @param[in] aQuery  an UTF-8 encoded SQL query
         *
         * @return a temporary Column object with the first column of result.
         *
         * @throw SQLite::Exception in case of error
         */
        inline Column execAndGet(const std::string& aQuery)
        {
            return execAndGet(aQuery.c_str());
        }

        /**
         * @brief Shortcut to test if a table exists.
         *
         *  Table names are case sensitive.
         *
         * @param[in] apTableName an UTF-8 encoded case sensitive Table name
         *
         * @return true if the table exists.
         *
         * @throw SQLite::Exception in case of error
         */
        bool tableExists(const char* apTableName);

        /**
         * @brief Shortcut to test if a table exists.
         *
         *  Table names are case sensitive.
         *
         * @param[in] aTableName an UTF-8 encoded case sensitive Table name
         *
         * @return true if the table exists.
         *
         * @throw SQLite::Exception in case of error
         */
        inline bool tableExists(const std::string& aTableName)
        {
            return tableExists(aTableName.c_str());
        }

        /**
         * @brief Get the rowid of the most recent successful INSERT into the database from the current connection.
         *
         *  Each entry in an SQLite table always has a unique 64-bit signed integer key called the rowid.
         * If the table has a column of type INTEGER PRIMARY KEY, then it is an alias for the rowid.
         *
         * @return Rowid of the most recent successful INSERT into the database, or 0 if there was none.
         */
        long long getLastInsertRowid() const noexcept; // nothrow

        /// Get total number of rows modified by all INSERT, UPDATE or DELETE statement since connection (not DROP table).
        int getTotalChanges() const noexcept; // nothrow

        /// Return the numeric result code for the most recent failed API call (if any).
        int getErrorCode() const noexcept; // nothrow
        /// Return the extended numeric result code for the most recent failed API call (if any).
        int getExtendedErrorCode() const noexcept; // nothrow
        /// Return UTF-8 encoded English language explanation of the most recent failed API call (if any).
        const char* getErrorMsg() const noexcept; // nothrow

        /// Return the filename used to open the database.
        const std::string& getFilename() const noexcept // nothrow
        {
            return mFilename;
        }

        /**
         * @brief Return raw pointer to SQLite Database Connection Handle.
         *
         * This is often needed to mix this wrapper with other libraries or for advance usage not supported by SQLiteCpp.
         */
        inline sqlite3* getHandle() const noexcept // nothrow
        {
            return mpSQLite;
        }

        /**
         * @brief Create or redefine a SQL function or aggregate in the sqlite database.
         *
         *  This is the equivalent of the sqlite3_create_function_v2 command.
         * @see http://www.sqlite.org/c3ref/create_function.html
         *
         * @note UTF-8 text encoding assumed.
         *
         * @param[in] apFuncName    Name of the SQL function to be created or redefined
         * @param[in] aNbArg        Number of arguments in the function
         * @param[in] abDeterministic Optimize for deterministic functions (most are). A random number generator is not.
         * @param[in] apApp         Arbitrary pointer of user data, accessible with sqlite3_user_data().
         * @param[in] apFunc        Pointer to a C-function to implement a scalar SQL function (apStep & apFinal NULL)
         * @param[in] apStep        Pointer to a C-function to implement an aggregate SQL function (apFunc NULL)
         * @param[in] apFinal       Pointer to a C-function to implement an aggregate SQL function (apFunc NULL)
         * @param[in] apDestroy     If not NULL, then it is the destructor for the application data pointer.
         *
         * @throw SQLite::Exception in case of error
         */
        void createFunction(const char* apFuncName,
                            int         aNbArg,
                            bool        abDeterministic,
                            void*       apApp,
                            void      (*apFunc)(sqlite3_context *, int, sqlite3_value **),
                            void      (*apStep)(sqlite3_context *, int, sqlite3_value **),
                            void      (*apFinal)(sqlite3_context *),  // NOLINT(readability/casting)
                            void      (*apDestroy)(void *));

        /**
         * @brief Create or redefine a SQL function or aggregate in the sqlite database.
         *
         *  This is the equivalent of the sqlite3_create_function_v2 command.
         * @see http://www.sqlite.org/c3ref/create_function.html
         *
         * @note UTF-8 text encoding assumed.
         *
         * @param[in] aFuncName     Name of the SQL function to be created or redefined
         * @param[in] aNbArg        Number of arguments in the function
         * @param[in] abDeterministic Optimize for deterministic functions (most are). A random number generator is not.
         * @param[in] apApp         Arbitrary pointer of user data, accessible with sqlite3_user_data().
         * @param[in] apFunc        Pointer to a C-function to implement a scalar SQL function (apStep & apFinal NULL)
         * @param[in] apStep        Pointer to a C-function to implement an aggregate SQL function (apFunc NULL)
         * @param[in] apFinal       Pointer to a C-function to implement an aggregate SQL function (apFunc NULL)
         * @param[in] apDestroy     If not NULL, then it is the destructor for the application data pointer.
         *
         * @throw SQLite::Exception in case of error
         */
        inline void createFunction(const std::string&   aFuncName,
                                   int                  aNbArg,
                                   bool                 abDeterministic,
                                   void*                apApp,
                                   void               (*apFunc)(sqlite3_context *, int, sqlite3_value **),
                                   void               (*apStep)(sqlite3_context *, int, sqlite3_value **),
                                   void               (*apFinal)(sqlite3_context *), // NOLINT(readability/casting)
                                   void               (*apDestroy)(void *))
        {
            return createFunction(aFuncName.c_str(), aNbArg, abDeterministic,
                                  apApp, apFunc, apStep, apFinal, apDestroy);
        }

        /**
         * @brief Load a module into the current sqlite database instance.
         *
         *  This is the equivalent of the sqlite3_load_extension call, but additionally enables
         *  module loading support prior to loading the requested module.
         *
         * @see http://www.sqlite.org/c3ref/load_extension.html
         *
         * @note UTF-8 text encoding assumed.
         *
         * @param[in] apExtensionName   Name of the shared library containing extension
         * @param[in] apEntryPointName  Name of the entry point (NULL to let sqlite work it out)
         *
         * @throw SQLite::Exception in case of error
         */
        void loadExtension(const char* apExtensionName, const char* apEntryPointName);

        /**
        * @brief Set the key for the current sqlite database instance.
        *
        *  This is the equivalent of the sqlite3_key call and should thus be called
        *  directly after opening the database.
        *  Open encrypted database -> call db.key("secret") -> database ready
        *
        * @param[in] aKey   Key to decode/encode the database
        *
        * @throw SQLite::Exception in case of error
        */
        void key(const std::string& aKey) const;

        /**
        * @brief Reset the key for the current sqlite database instance.
        *
        *  This is the equivalent of the sqlite3_rekey call and should thus be called
        *  after the database has been opened with a valid key. To decrypt a
        *  database, call this method with an empty string.
        *  Open normal database -> call db.rekey("secret") -> encrypted database, database ready
        *  Open encrypted database -> call db.key("secret") -> call db.rekey("newsecret") -> change key, database ready
        *  Open encrypted database -> call db.key("secret") -> call db.rekey("") -> decrypted database, database ready
        *
        * @param[in] aNewKey   New key to encode the database
        *
        * @throw SQLite::Exception in case of error
        */
        void rekey(const std::string& aNewKey) const;

        /**
        * @brief Test if a file contains an unencrypted database.
        *
        *  This is a simple test that reads the first bytes of a database file and
        *  compares them to the standard header for unencrypted databases. If the
        *  header does not match the standard string, we assume that we have an
        *  encrypted file.
        *
        * @param[in] aFilename path/uri to a file
        *
        * @return true if the database has the standard header.
        *
        * @throw SQLite::Exception in case of error
        */
        static bool isUnencrypted(const std::string& aFilename);

    private:
        /// @{ Database must be non-copyable
        Database(const Database&);
        Database& operator=(const Database&);
        /// @}

        /**
         * @brief Check if aRet equal SQLITE_OK, else throw a SQLite::Exception with the SQLite error message
         */
        inline void check(const int aRet) const
        {
            if (SQLite::OK != aRet)
            {
                throw SQLite::Exception(mpSQLite, aRet);
            }
        }

    private:
        sqlite3*    mpSQLite;   ///< Pointer to SQLite Database Connection Handle
        std::string mFilename;  ///< UTF-8 filename used to open the database
    };


}  // namespace SQLite
/**
 * @file    Backup.h
 * @ingroup SQLiteCpp
 * @brief   Backup is used to backup a database file in a safe and online way.
 *
 * Copyright (c) 2015 Shibao HONG (shibaohong@outlook.com)
 * Copyright (c) 2015-2016 Sebastien Rombauts (sebastien.rombauts@gmail.com)
 *
 * Distributed under the MIT License (MIT) (See accompanying file LICENSE.txt
 * or copy at http://opensource.org/licenses/MIT)
 */



// Forward declaration to avoid inclusion of <sqlite3.h> in a header
struct sqlite3_backup;

namespace SQLite
{

/**
 * @brief RAII encapsulation of a SQLite Database Backup process.
 *
 * A Backup object is used to backup a source database file to a destination database file
 * in a safe and online way.
 *
 * Resource Acquisition Is Initialization (RAII) means that the Backup Resource
 * is allocated in the constructor and released in the destructor, so that there is
 * no need to worry about memory management or the validity of the underlying SQLite Backup.
 *
 * Thread-safety: a Backup object shall not be shared by multiple threads, because :
 * 1) in the SQLite "Thread Safe" mode, "SQLite can be safely used by multiple threads
 *    provided that no single database connection is used simultaneously in two or more threads."
 * 2) the SQLite "Serialized" mode is not supported by SQLiteC++,
 *    because of the way it shares the underling SQLite precompiled statement
 *    in a custom shared pointer (See the inner class "Statement::Ptr").
 */
    class Backup
    {
    public:
        /**
         * @brief Initialize a SQLite Backup object.
         *
         * Initialize a SQLite Backup object for the source database and destination database.
         * The database name is "main" for the main database, "temp" for the temporary database,
         * or the name specified after the AS keyword in an ATTACH statement for an attached database.
         *
         * Exception is thrown in case of error, then the Backup object is NOT constructed.
         *
         * @param[in] aDestDatabase        Destination database connection
         * @param[in] apDestDatabaseName   Destination database name
         * @param[in] aSrcDatabase         Source database connection
         * @param[in] apSrcDatabaseName    Source database name
         *
         * @throw SQLite::Exception in case of error
         */
        Backup(Database&   aDestDatabase,
               const char* apDestDatabaseName,
               Database&   aSrcDatabase,
               const char* apSrcDatabaseName);

        /**
         * @brief Initialize a SQLite Backup object.
         *
         * Initialize a SQLite Backup object for source database and destination database.
         * The database name is "main" for the main database, "temp" for the temporary database,
         * or the name specified after the AS keyword in an ATTACH statement for an attached database.
         *
         * Exception is thrown in case of error, then the Backup object is NOT constructed.
         *
         * @param[in] aDestDatabase        Destination database connection
         * @param[in] aDestDatabaseName    Destination database name
         * @param[in] aSrcDatabase         Source database connection
         * @param[in] aSrcDatabaseName     Source database name
         *
         * @throw SQLite::Exception in case of error
         */
        Backup(Database&          aDestDatabase,
               const std::string& aDestDatabaseName,
               Database&          aSrcDatabase,
               const std::string& aSrcDatabaseName);

        /**
         * @brief Initialize a SQLite Backup object for main databases.
         *
         * Initialize a SQLite Backup object for source database and destination database.
         * Backup the main databases between the source and the destination.
         *
         * Exception is thrown in case of error, then the Backup object is NOT constructed.
         *
         * @param[in] aDestDatabase        Destination database connection
         * @param[in] aSrcDatabase         Source database connection
         *
         * @throw SQLite::Exception in case of error
         */
        Backup(Database& aDestDatabase,
               Database& aSrcDatabase);

        /// Release the SQLite Backup resource.
        virtual ~Backup() noexcept;

        /**
         * @brief Execute a step of backup with a given number of source pages to be copied
         *
         * Exception is thrown when SQLITE_IOERR_XXX, SQLITE_NOMEM, or SQLITE_READONLY is returned
         * in sqlite3_backup_step(). These errors are considered fatal, so there is no point
         * in retrying the call to executeStep().
         *
         * @param[in] aNumPage    The number of source pages to be copied, with a negative value meaning all remaining source pages
         *
         * @return SQLITE_OK/SQLITE_DONE/SQLITE_BUSY/SQLITE_LOCKED
         *
         * @throw SQLite::Exception in case of error
         */
        int executeStep(const int aNumPage = -1);

        /// Return the number of source pages still to be backed up as of the most recent call to executeStep().
        int getRemainingPageCount();

        /// Return the total number of pages in the source database as of the most recent call to executeStep().
        int getTotalPageCount();

    private:
        /// @{ Backup must be non-copyable
        Backup(const Backup&);
        Backup& operator=(const Backup&);
        /// @}

    private:
        sqlite3_backup* mpSQLiteBackup;   ///< Pointer to SQLite Database Backup Handle
    };

}  // namespace SQLite
/**
 * @file    SQLiteCpp.h
 * @ingroup SQLiteCpp
 * @brief   SQLiteC++ is a smart and simple C++ SQLite3 wrapper. This file is only "easy include" for other files.
 *
 * Include this main header file in your project to gain access to all functionality provided by the wrapper.
 *
 * Copyright (c) 2012-2016 Sebastien Rombauts (sebastien.rombauts@gmail.com)
 *
 * Distributed under the MIT License (MIT) (See accompanying file LICENSE.txt
 * or copy at http://opensource.org/licenses/MIT)
 */
/**
 * @defgroup SQLiteCpp SQLiteC++
 * @brief    SQLiteC++ is a smart and simple C++ SQLite3 wrapper. This file is only "easy include" for other files.
 */


// Include useful headers of SQLiteC++


/**
 * @brief Version numbers for SQLiteC++ are provided in the same way as sqlite3.h
 *
 * The [SQLITECPP_VERSION] C preprocessor macro in the SQLiteC++.h header
 * evaluates to a string literal that is the SQLite version in the
 * format "X.Y.Z" where X is the major version number
 * and Y is the minor version number and Z is the release number.
 *
 * The [SQLITECPP_VERSION_NUMBER] C preprocessor macro resolves to an integer
 * with the value (X*1000000 + Y*1000 + Z) where X, Y, and Z are the same
 * numbers used in [SQLITECPP_VERSION].
 */
#define SQLITECPP_VERSION           "2.01.00"   // 2.0.0
#define SQLITECPP_VERSION_NUMBER     2001000    // 2.0.0
/**
 * @file    Transaction.h
 * @ingroup SQLiteCpp
 * @brief   A Transaction is way to group multiple SQL statements into an atomic secured operation.
 *
 * Copyright (c) 2012-2016 Sebastien Rombauts (sebastien.rombauts@gmail.com)
 *
 * Distributed under the MIT License (MIT) (See accompanying file LICENSE.txt
 * or copy at http://opensource.org/licenses/MIT)
 */



namespace SQLite
{


// Forward declaration
    class Database;

/**
 * @brief RAII encapsulation of a SQLite Transaction.
 *
 * A Transaction is a way to group multiple SQL statements into an atomic secured operation;
 * either it succeeds, with all the changes committed to the database file,
 * or if it fails, all the changes are rolled back to the initial state.
 *
 * Resource Acquisition Is Initialization (RAII) means that the Transaction
 * begins in the constructor and is rollbacked in the destructor, so that there is
 * no need to worry about memory management or the validity of the underlying SQLite Connection.
 *
 * This method also offers big performances improvements compared to individually executed statements.
 *
 * Thread-safety: a Transaction object shall not be shared by multiple threads, because :
 * 1) in the SQLite "Thread Safe" mode, "SQLite can be safely used by multiple threads
 *    provided that no single database connection is used simultaneously in two or more threads."
 * 2) the SQLite "Serialized" mode is not supported by SQLiteC++,
 *    because of the way it shares the underling SQLite precompiled statement
 *    in a custom shared pointer (See the inner class "Statement::Ptr").
 */
    class Transaction
    {
    public:
        /**
         * @brief Begins the SQLite transaction
         *
         * @param[in] aDatabase the SQLite Database Connection
         *
         * Exception is thrown in case of error, then the Transaction is NOT initiated.
         */
        explicit Transaction(Database& aDatabase);

        /**
         * @brief Safely rollback the transaction if it has not been committed.
         */
        virtual ~Transaction() noexcept; // nothrow

        /**
         * @brief Commit the transaction.
         */
        void commit();

    private:
        // Transaction must be non-copyable
        Transaction(const Transaction&);
        Transaction& operator=(const Transaction&);
        /// @}

    private:
        Database&   mDatabase;  ///< Reference to the SQLite Database Connection
        bool        mbCommited; ///< True when commit has been called
    };


}  // namespace SQLite
/**
 * @file    Backup.cpp
 * @ingroup SQLiteCpp
 * @brief   Backup is used to backup a database file in a safe and online way.
 *
 * Copyright (c) 2015 Shibao HONG (shibaohong@outlook.com)
 * Copyright (c) 2015-2016 Sebastien Rombauts (sebastien.rombauts@gmail.com)
 *
 * Distributed under the MIT License (MIT) (See accompanying file LICENSE.txt
 * or copy at http://opensource.org/licenses/MIT)
 */



namespace SQLite
{

// Initialize resource for SQLite database backup
    Backup::Backup(Database&    aDestDatabase,
                   const char*  apDestDatabaseName,
                   Database&    aSrcDatabase,
                   const char*  apSrcDatabaseName) :
            mpSQLiteBackup(NULL)
    {
        mpSQLiteBackup = sqlite3_backup_init(aDestDatabase.getHandle(),
                                             apDestDatabaseName,
                                             aSrcDatabase.getHandle(),
                                             apSrcDatabaseName);
        if (NULL == mpSQLiteBackup)
        {
            // If an error occurs, the error code and message are attached to the destination database connection.
            throw SQLite::Exception(aDestDatabase.getHandle());
        }
    }

// Initialize resource for SQLite database backup
    Backup::Backup(Database&            aDestDatabase,
                   const std::string&   aDestDatabaseName,
                   Database&            aSrcDatabase,
                   const std::string&   aSrcDatabaseName) :
            mpSQLiteBackup(NULL)
    {
        mpSQLiteBackup = sqlite3_backup_init(aDestDatabase.getHandle(),
                                             aDestDatabaseName.c_str(),
                                             aSrcDatabase.getHandle(),
                                             aSrcDatabaseName.c_str());
        if (NULL == mpSQLiteBackup)
        {
            // If an error occurs, the error code and message are attached to the destination database connection.
            throw SQLite::Exception(aDestDatabase.getHandle());
        }
    }

// Initialize resource for SQLite database backup
    Backup::Backup(Database &aDestDatabase, Database &aSrcDatabase) :
            mpSQLiteBackup(NULL)
    {
        mpSQLiteBackup = sqlite3_backup_init(aDestDatabase.getHandle(),
                                             "main",
                                             aSrcDatabase.getHandle(),
                                             "main");
        if (NULL == mpSQLiteBackup)
        {
            // If an error occurs, the error code and message are attached to the destination database connection.
            throw SQLite::Exception(aDestDatabase.getHandle());
        }
    }

// Release resource for SQLite database backup
    Backup::~Backup() noexcept
    {
        if (NULL != mpSQLiteBackup)
        {
            sqlite3_backup_finish(mpSQLiteBackup);
        }
    }

// Execute backup step with a given number of source pages to be copied
    int Backup::executeStep(const int aNumPage /* = -1 */)
    {
        const int res = sqlite3_backup_step(mpSQLiteBackup, aNumPage);
        if (SQLITE_OK != res && SQLITE_DONE != res && SQLITE_BUSY != res && SQLITE_LOCKED != res)
        {
            throw SQLite::Exception(sqlite3_errstr(res), res);
        }
        return res;
    }

// Get the number of remaining source pages to be copied in this backup process
    int Backup::getRemainingPageCount()
    {
        return sqlite3_backup_remaining(mpSQLiteBackup);
    }

// Get the number of total source pages to be copied in this backup process
    int Backup::getTotalPageCount()
    {
        return sqlite3_backup_pagecount(mpSQLiteBackup);
    }

}  // namespace SQLite
/**
 * @file    Column.cpp
 * @ingroup SQLiteCpp
 * @brief   Encapsulation of a Column in a row of the result pointed by the prepared SQLite::Statement.
 *
 * Copyright (c) 2012-2016 Sebastien Rombauts (sebastien.rombauts@gmail.com)
 *
 * Distributed under the MIT License (MIT) (See accompanying file LICENSE.txt
 * or copy at http://opensource.org/licenses/MIT)
 */




namespace SQLite
{

    const int INTEGER   = SQLITE_INTEGER;
    const int FLOAT     = SQLITE_FLOAT;
    const int TEXT      = SQLITE_TEXT;
    const int BLOB      = SQLITE_BLOB;
    const int Null      = SQLITE_NULL;


// Encapsulation of a Column in a row of the result pointed by the prepared Statement.
    Column::Column(Statement::Ptr& aStmtPtr, int aIndex) noexcept : // nothrow
            mStmtPtr(aStmtPtr),
            mIndex(aIndex)
    {
    }

// Finalize and unregister the SQL query from the SQLite Database Connection.
    Column::~Column() noexcept // nothrow
    {
        // the finalization will be done by the destructor of the last shared pointer
    }

// Return the named assigned to this result column (potentially aliased)
    const char* Column::getName() const noexcept // nothrow
    {
        return sqlite3_column_name(mStmtPtr, mIndex);
    }

#ifdef SQLITE_ENABLE_COLUMN_METADATA
    // Return the name of the table column that is the origin of this result column
const char* Column::getOriginName() const noexcept // nothrow
{
    return sqlite3_column_origin_name(mStmtPtr, mIndex);
}
#endif

// Return the integer value of the column specified by its index starting at 0
    int Column::getInt() const noexcept // nothrow
    {
        return sqlite3_column_int(mStmtPtr, mIndex);
    }

// Return the unsigned integer value of the column specified by its index starting at 0
    unsigned Column::getUInt() const noexcept // nothrow
    {
        return static_cast<unsigned>(getInt64());
    }

// Return the 64bits integer value of the column specified by its index starting at 0
    long long Column::getInt64() const noexcept // nothrow
    {
        return sqlite3_column_int64(mStmtPtr, mIndex);
    }

// Return the double value of the column specified by its index starting at 0
    double Column::getDouble() const noexcept // nothrow
    {
        return sqlite3_column_double(mStmtPtr, mIndex);
    }

// Return a pointer to the text value (NULL terminated string) of the column specified by its index starting at 0
    const char* Column::getText(const char* apDefaultValue /* = "" */) const noexcept // nothrow
    {
        const char* pText = reinterpret_cast<const char*>(sqlite3_column_text(mStmtPtr, mIndex));
        return (pText?pText:apDefaultValue);
    }

// Return a pointer to the blob value (*not* NULL terminated) of the column specified by its index starting at 0
    const void* Column::getBlob() const noexcept // nothrow
    {
        return sqlite3_column_blob(mStmtPtr, mIndex);
    }

// Return a std::string to a TEXT or BLOB column
    std::string Column::getString() const noexcept // nothrow
    {
        // Note: using sqlite3_column_blob and not sqlite3_column_text
        // - no need for sqlite3_column_text to add a \0 on the end, as we're getting the bytes length directly
        const char *data = static_cast<const char *>(sqlite3_column_blob(mStmtPtr, mIndex));

        // SQLite docs: "The safest policy is to invoke… sqlite3_column_blob() followed by sqlite3_column_bytes()"
        // Note: std::string is ok to pass nullptr as first arg, if length is 0
        return std::string(data, sqlite3_column_bytes(mStmtPtr, mIndex));
    }

// Return the type of the value of the column
    int Column::getType() const noexcept // nothrow
    {
        return sqlite3_column_type(mStmtPtr, mIndex);
    }

// Return the number of bytes used by the text value of the column
    int Column::getBytes() const noexcept // nothrow
    {
        return sqlite3_column_bytes(mStmtPtr, mIndex);
    }

// Standard std::ostream inserter
    std::ostream& operator<<(std::ostream& aStream, const Column& aColumn)
    {
        aStream << aColumn.getText();
        return aStream;
    }


}  // namespace SQLite
/**
 * @file    Database.cpp
 * @ingroup SQLiteCpp
 * @brief   Management of a SQLite Database Connection.
 *
 * Copyright (c) 2012-2016 Sebastien Rombauts (sebastien.rombauts@gmail.com)
 *
 * Distributed under the MIT License (MIT) (See accompanying file LICENSE.txt
 * or copy at http://opensource.org/licenses/MIT)
 */



#ifndef SQLITE_DETERMINISTIC
#define SQLITE_DETERMINISTIC 0x800
#endif // SQLITE_DETERMINISTIC


namespace SQLite
{

    const int   OPEN_READONLY   = SQLITE_OPEN_READONLY;
    const int   OPEN_READWRITE  = SQLITE_OPEN_READWRITE;
    const int   OPEN_CREATE     = SQLITE_OPEN_CREATE;
    const int   OPEN_URI        = SQLITE_OPEN_URI;

    const int   OK              = SQLITE_OK;

    const char* VERSION         = SQLITE_VERSION;
    const int   VERSION_NUMBER  = SQLITE_VERSION_NUMBER;

// Return SQLite version string using runtime call to the compiled library
    const char* getLibVersion() noexcept // nothrow
    {
        return sqlite3_libversion();
    }

// Return SQLite version number using runtime call to the compiled library
    int getLibVersionNumber() noexcept // nothrow
    {
        return sqlite3_libversion_number();
    }


// Open the provided database UTF-8 filename with SQLite::OPEN_xxx provided flags.
    Database::Database(const char* apFilename,
                       const int   aFlags         /* = SQLite::OPEN_READONLY*/,
                       const int   aBusyTimeoutMs /* = 0 */,
                       const char* apVfs          /* = NULL*/) :
            mpSQLite(NULL),
            mFilename(apFilename)
    {
        const int ret = sqlite3_open_v2(apFilename, &mpSQLite, aFlags, apVfs);
        if (SQLITE_OK != ret)
        {
            const SQLite::Exception exception(mpSQLite, ret); // must create before closing
            sqlite3_close(mpSQLite); // close is required even in case of error on opening
            throw exception;
        }
        if (aBusyTimeoutMs > 0)
        {
            setBusyTimeout(aBusyTimeoutMs);
        }
    }

// Open the provided database UTF-8 filename with SQLite::OPEN_xxx provided flags.
    Database::Database(const std::string& aFilename,
                       const int          aFlags         /* = SQLite::OPEN_READONLY*/,
                       const int          aBusyTimeoutMs /* = 0 */,
                       const std::string& aVfs           /* = "" */) :
            mpSQLite(NULL),
            mFilename(aFilename)
    {
        const int ret = sqlite3_open_v2(aFilename.c_str(), &mpSQLite, aFlags, aVfs.empty() ? NULL : aVfs.c_str());
        if (SQLITE_OK != ret)
        {
            const SQLite::Exception exception(mpSQLite, ret); // must create before closing
            sqlite3_close(mpSQLite); // close is required even in case of error on opening
            throw exception;
        }
        if (aBusyTimeoutMs > 0)
        {
            setBusyTimeout(aBusyTimeoutMs);
        }
    }

// Close the SQLite database connection.
    Database::~Database() noexcept // nothrow
    {
        const int ret = sqlite3_close(mpSQLite);

        // Avoid unreferenced variable warning when build in release mode
        (void) ret;

        // Only case of error is SQLITE_BUSY: "database is locked" (some statements are not finalized)
        // Never throw an exception in a destructor :
        SQLITECPP_ASSERT(SQLITE_OK == ret, "database is locked");  // See SQLITECPP_ENABLE_ASSERT_HANDLER
    }

/**
 * @brief Set a busy handler that sleeps for a specified amount of time when a table is locked.
 *
 *  This is useful in multithreaded program to handle case where a table is locked for writting by a thread.
 *  Any other thread cannot access the table and will receive a SQLITE_BUSY error:
 *  setting a timeout will wait and retry up to the time specified before returning this SQLITE_BUSY error.
 *  Reading the value of timeout for current connection can be done with SQL query "PRAGMA busy_timeout;".
 *  Default busy timeout is 0ms.
 *
 * @param[in] aBusyTimeoutMs    Amount of milliseconds to wait before returning SQLITE_BUSY
 *
 * @throw SQLite::Exception in case of error
 */
    void Database::setBusyTimeout(const int aBusyTimeoutMs) noexcept // nothrow
    {
        const int ret = sqlite3_busy_timeout(mpSQLite, aBusyTimeoutMs);
        check(ret);
    }

// Shortcut to execute one or multiple SQL statements without results (UPDATE, INSERT, ALTER, COMMIT, CREATE...).
    int Database::exec(const char* apQueries)
    {
        const int ret = sqlite3_exec(mpSQLite, apQueries, NULL, NULL, NULL);
        check(ret);

        // Return the number of rows modified by those SQL statements (INSERT, UPDATE or DELETE only)
        return sqlite3_changes(mpSQLite);
    }

// Shortcut to execute a one step query and fetch the first column of the result.
// WARNING: Be very careful with this dangerous method: you have to
// make a COPY OF THE result, else it will be destroy before the next line
// (when the underlying temporary Statement and Column objects are destroyed)
// this is an issue only for pointer type result (ie. char* and blob)
// (use the Column copy-constructor)
    Column Database::execAndGet(const char* apQuery)
    {
        Statement query(*this, apQuery);
        (void)query.executeStep(); // Can return false if no result, which will throw next line in getColumn()
        return query.getColumn(0);
    }

// Shortcut to test if a table exists.
    bool Database::tableExists(const char* apTableName)
    {
        Statement query(*this, "SELECT count(*) FROM sqlite_master WHERE type='table' AND name=?");
        query.bind(1, apTableName);
        (void)query.executeStep(); // Cannot return false, as the above query always return a result
        return (1 == query.getColumn(0).getInt());
    }

// Get the rowid of the most recent successful INSERT into the database from the current connection.
    long long Database::getLastInsertRowid() const noexcept // nothrow
    {
        return sqlite3_last_insert_rowid(mpSQLite);
    }

// Get total number of rows modified by all INSERT, UPDATE or DELETE statement since connection.
    int Database::getTotalChanges() const noexcept // nothrow
    {
        return sqlite3_total_changes(mpSQLite);
    }

// Return the numeric result code for the most recent failed API call (if any).
    int Database::getErrorCode() const noexcept // nothrow
    {
        return sqlite3_errcode(mpSQLite);
    }

// Return the extended numeric result code for the most recent failed API call (if any).
    int Database::getExtendedErrorCode() const noexcept // nothrow
    {
        return sqlite3_extended_errcode(mpSQLite);
    }

// Return UTF-8 encoded English language explanation of the most recent failed API call (if any).
    const char* Database::getErrorMsg() const noexcept // nothrow
    {
        return sqlite3_errmsg(mpSQLite);
    }

// Attach a custom function to your sqlite database. Assumes UTF8 text representation.
// Parameter details can be found here: http://www.sqlite.org/c3ref/create_function.html
    void Database::createFunction(const char*   apFuncName,
                                  int           aNbArg,
                                  bool          abDeterministic,
                                  void*         apApp,
                                  void        (*apFunc)(sqlite3_context *, int, sqlite3_value **),
                                  void        (*apStep)(sqlite3_context *, int, sqlite3_value **),
                                  void        (*apFinal)(sqlite3_context *),   // NOLINT(readability/casting)
                                  void        (*apDestroy)(void *))
    {
        int TextRep = SQLITE_UTF8;
        // optimization if deterministic function (e.g. of nondeterministic function random())
        if (abDeterministic) {
            TextRep = TextRep|SQLITE_DETERMINISTIC;
        }
        const int ret = sqlite3_create_function_v2(mpSQLite, apFuncName, aNbArg, TextRep,
                                                   apApp, apFunc, apStep, apFinal, apDestroy);
        check(ret);
    }

// Load an extension into the sqlite database. Only affects the current connection.
// Parameter details can be found here: http://www.sqlite.org/c3ref/load_extension.html
    void Database::loadExtension(const char* apExtensionName, const char *apEntryPointName)
    {
#ifdef SQLITE_OMIT_LOAD_EXTENSION
        throw std::runtime_error("sqlite extensions are disabled");
#else
#ifdef SQLITE_DBCONFIG_ENABLE_LOAD_EXTENSION // Since SQLite 3.13 (2016-05-18):
        // Security warning:
    // It is recommended that the SQLITE_DBCONFIG_ENABLE_LOAD_EXTENSION method be used to enable only this interface.
    // The use of the sqlite3_enable_load_extension() interface should be avoided to keep the SQL load_extension()
    // disabled and prevent SQL injections from giving attackers access to extension loading capabilities.
    int ret = sqlite3_db_config(mpSQLite, SQLITE_DBCONFIG_ENABLE_LOAD_EXTENSION, 1, NULL);
#else
        int ret = sqlite3_enable_load_extension(mpSQLite, 1);
#endif
        check(ret);

        ret = sqlite3_load_extension(mpSQLite, apExtensionName, apEntryPointName, 0);
        check(ret);
#endif
    }

// Set the key for the current sqlite database instance.
    void Database::key(const std::string& aKey) const
    {
        int pass_len = aKey.length();
#ifdef SQLITE_HAS_CODEC
        if (pass_len > 0) {
        const int ret = sqlite3_key(mpSQLite, aKey.c_str(), pass_len);
        check(ret);
    }
#else // SQLITE_HAS_CODEC
        if (pass_len > 0) {
            const SQLite::Exception exception("No encryption support, recompile with SQLITE_HAS_CODEC to enable.");
            throw exception;
        }
#endif // SQLITE_HAS_CODEC
    }

// Reset the key for the current sqlite database instance.
    void Database::rekey(const std::string& aNewKey) const
    {
#ifdef SQLITE_HAS_CODEC
        int pass_len = aNewKey.length();
    if (pass_len > 0) {
        const int ret = sqlite3_rekey(mpSQLite, aNewKey.c_str(), pass_len);
        check(ret);
    } else {
        const int ret = sqlite3_rekey(mpSQLite, nullptr, 0);
        check(ret);
    }
#else // SQLITE_HAS_CODEC
        static_cast<void>(aNewKey); // silence unused parameter warning
        const SQLite::Exception exception("No encryption support, recompile with SQLITE_HAS_CODEC to enable.");
        throw exception;
#endif // SQLITE_HAS_CODEC
    }

// Test if a file contains an unencrypted database.
    bool Database::isUnencrypted(const std::string& aFilename)
    {
        if (aFilename.length() > 0) {
            std::ifstream fileBuffer(aFilename.c_str(), std::ios::in | std::ios::binary);
            char header[16];
            if (fileBuffer.is_open()) {
                fileBuffer.seekg(0, std::ios::beg);
                fileBuffer.getline(header, 16);
                fileBuffer.close();
            } else {
                const SQLite::Exception exception("Error opening file: " + aFilename);
                throw exception;
            }
            return strncmp(header, "SQLite format 3\000", 16) == 0;
        }
        const SQLite::Exception exception("Could not open database, the aFilename parameter was empty.");
        throw exception;
    }

}  // namespace SQLite
/**
 * @file    Exception.cpp
 * @ingroup SQLiteCpp
 * @brief   Encapsulation of the error message from SQLite3 on a std::runtime_error.
 *
 * Copyright (c) 2012-2016 Sebastien Rombauts (sebastien.rombauts@gmail.com)
 *
 * Distributed under the MIT License (MIT) (See accompanying file LICENSE.txt
 * or copy at http://opensource.org/licenses/MIT)
 */



namespace SQLite
{

    Exception::Exception(const std::string& aErrorMessage) :
            std::runtime_error(aErrorMessage),
            mErrcode(-1), // 0 would be SQLITE_OK, which doesn't make sense
            mExtendedErrcode(-1)
    {
    }

    Exception::Exception(const std::string& aErrorMessage, int ret) :
            std::runtime_error(aErrorMessage),
            mErrcode(ret),
            mExtendedErrcode(-1)
    {
    }

    Exception::Exception(sqlite3* apSQLite) :
            std::runtime_error(sqlite3_errmsg(apSQLite)),
            mErrcode(sqlite3_errcode(apSQLite)),
            mExtendedErrcode(sqlite3_extended_errcode(apSQLite))
    {
    }

    Exception::Exception(sqlite3* apSQLite, int ret) :
            std::runtime_error(sqlite3_errmsg(apSQLite)),
            mErrcode(ret),
            mExtendedErrcode(sqlite3_extended_errcode(apSQLite))
    {
    }

// Return a string, solely based on the error code
    const char* Exception::getErrorStr() const noexcept // nothrow
    {
        return sqlite3_errstr(mErrcode);
    }


}  // namespace SQLite
/**
 * @file    Statement.cpp
 * @ingroup SQLiteCpp
 * @brief   A prepared SQLite Statement is a compiled SQL query ready to be executed, pointing to a row of result.
 *
 * Copyright (c) 2012-2016 Sebastien Rombauts (sebastien.rombauts@gmail.com)
 *
 * Distributed under the MIT License (MIT) (See accompanying file LICENSE.txt
 * or copy at http://opensource.org/licenses/MIT)
 */



namespace SQLite
{

// Compile and register the SQL query for the provided SQLite Database Connection
    Statement::Statement(Database &aDatabase, const char* apQuery) :
            mQuery(apQuery),
            mStmtPtr(aDatabase.mpSQLite, mQuery), // prepare the SQL query, and ref count (needs Database friendship)
            mColumnCount(0),
            mbOk(false),
            mbDone(false)
    {
        mColumnCount = sqlite3_column_count(mStmtPtr);
    }

// Compile and register the SQL query for the provided SQLite Database Connection
    Statement::Statement(Database &aDatabase, const std::string& aQuery) :
            mQuery(aQuery),
            mStmtPtr(aDatabase.mpSQLite, mQuery), // prepare the SQL query, and ref count (needs Database friendship)
            mColumnCount(0),
            mbOk(false),
            mbDone(false)
    {
        mColumnCount = sqlite3_column_count(mStmtPtr);
    }


// Finalize and unregister the SQL query from the SQLite Database Connection.
    Statement::~Statement() noexcept // nothrow
    {
        // the finalization will be done by the destructor of the last shared pointer
    }

// Reset the statement to make it ready for a new execution (see also #clearBindings() bellow)
    void Statement::reset()
    {
        mbOk = false;
        mbDone = false;
        const int ret = sqlite3_reset(mStmtPtr);
        check(ret);
    }

// Clears away all the bindings of a prepared statement (can be associated with #reset() above).
    void Statement::clearBindings()
    {
        const int ret = sqlite3_clear_bindings(mStmtPtr);
        check(ret);
    }

// Bind an int value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bind(const int aIndex, const int aValue)
    {
        const int ret = sqlite3_bind_int(mStmtPtr, aIndex, aValue);
        check(ret);
    }

// Bind a 32bits unsigned int value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bind(const int aIndex, const unsigned aValue)
    {
        const int ret = sqlite3_bind_int64(mStmtPtr, aIndex, aValue);
        check(ret);
    }

// Bind a 64bits int value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bind(const int aIndex, const long long aValue)
    {
        const int ret = sqlite3_bind_int64(mStmtPtr, aIndex, aValue);
        check(ret);
    }

// Bind a double (64bits float) value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bind(const int aIndex, const double aValue)
    {
        const int ret = sqlite3_bind_double(mStmtPtr, aIndex, aValue);
        check(ret);
    }

// Bind a string value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bind(const int aIndex, const std::string& aValue)
    {
        const int ret = sqlite3_bind_text(mStmtPtr, aIndex, aValue.c_str(),
                                          static_cast<int>(aValue.size()), SQLITE_TRANSIENT);
        check(ret);
    }

// Bind a text value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bind(const int aIndex, const char* apValue)
    {
        const int ret = sqlite3_bind_text(mStmtPtr, aIndex, apValue, -1, SQLITE_TRANSIENT);
        check(ret);
    }

// Bind a binary blob value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bind(const int aIndex, const void* apValue, const int aSize)
    {
        const int ret = sqlite3_bind_blob(mStmtPtr, aIndex, apValue, aSize, SQLITE_TRANSIENT);
        check(ret);
    }

// Bind a string value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bindNoCopy(const int aIndex, const std::string& aValue)
    {
        const int ret = sqlite3_bind_text(mStmtPtr, aIndex, aValue.c_str(),
                                          static_cast<int>(aValue.size()), SQLITE_STATIC);
        check(ret);
    }

// Bind a text value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bindNoCopy(const int aIndex, const char* apValue)
    {
        const int ret = sqlite3_bind_text(mStmtPtr, aIndex, apValue, -1, SQLITE_STATIC);
        check(ret);
    }

// Bind a binary blob value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bindNoCopy(const int aIndex, const void* apValue, const int aSize)
    {
        const int ret = sqlite3_bind_blob(mStmtPtr, aIndex, apValue, aSize, SQLITE_STATIC);
        check(ret);
    }

// Bind a NULL value to a parameter "?", "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bind(const int aIndex)
    {
        const int ret = sqlite3_bind_null(mStmtPtr, aIndex);
        check(ret);
    }


// Bind an int value to a parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bind(const char* apName, const int aValue)
    {
        const int index = sqlite3_bind_parameter_index(mStmtPtr, apName);
        const int ret = sqlite3_bind_int(mStmtPtr, index, aValue);
        check(ret);
    }

// Bind a 32bits unsigned int value to a parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bind(const char* apName, const unsigned aValue)
    {
        const int index = sqlite3_bind_parameter_index(mStmtPtr, apName);
        const int ret = sqlite3_bind_int64(mStmtPtr, index, aValue);
        check(ret);
    }

// Bind a 64bits int value to a parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bind(const char* apName, const long long aValue)
    {
        const int index = sqlite3_bind_parameter_index(mStmtPtr, apName);
        const int ret = sqlite3_bind_int64(mStmtPtr, index, aValue);
        check(ret);
    }

// Bind a double (64bits float) value to a parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bind(const char* apName, const double aValue)
    {
        const int index = sqlite3_bind_parameter_index(mStmtPtr, apName);
        const int ret = sqlite3_bind_double(mStmtPtr, index, aValue);
        check(ret);
    }

// Bind a string value to a parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bind(const char* apName, const std::string& aValue)
    {
        const int index = sqlite3_bind_parameter_index(mStmtPtr, apName);
        const int ret = sqlite3_bind_text(mStmtPtr, index, aValue.c_str(),
                                          static_cast<int>(aValue.size()), SQLITE_TRANSIENT);
        check(ret);
    }

// Bind a text value to a parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bind(const char* apName, const char* apValue)
    {
        const int index = sqlite3_bind_parameter_index(mStmtPtr, apName);
        const int ret = sqlite3_bind_text(mStmtPtr, index, apValue, -1, SQLITE_TRANSIENT);
        check(ret);
    }

// Bind a binary blob value to a parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bind(const char* apName, const void* apValue, const int aSize)
    {
        const int index = sqlite3_bind_parameter_index(mStmtPtr, apName);
        const int ret = sqlite3_bind_blob(mStmtPtr, index, apValue, aSize, SQLITE_TRANSIENT);
        check(ret);
    }

// Bind a string value to a parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bindNoCopy(const char* apName, const std::string& aValue)
    {
        const int index = sqlite3_bind_parameter_index(mStmtPtr, apName);
        const int ret = sqlite3_bind_text(mStmtPtr, index, aValue.c_str(),
                                          static_cast<int>(aValue.size()), SQLITE_STATIC);
        check(ret);
    }

// Bind a text value to a parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bindNoCopy(const char* apName, const char* apValue)
    {
        const int index = sqlite3_bind_parameter_index(mStmtPtr, apName);
        const int ret = sqlite3_bind_text(mStmtPtr, index, apValue, -1, SQLITE_STATIC);
        check(ret);
    }

// Bind a binary blob value to a parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bindNoCopy(const char* apName, const void* apValue, const int aSize)
    {
        const int index = sqlite3_bind_parameter_index(mStmtPtr, apName);
        const int ret = sqlite3_bind_blob(mStmtPtr, index, apValue, aSize, SQLITE_STATIC);
        check(ret);
    }

// Bind a NULL value to a parameter "?NNN", ":VVV", "@VVV" or "$VVV" in the SQL prepared statement
    void Statement::bind(const char* apName)
    {
        const int index = sqlite3_bind_parameter_index(mStmtPtr, apName);
        const int ret = sqlite3_bind_null(mStmtPtr, index);
        check(ret);
    }


// Execute a step of the query to fetch one row of results
    bool Statement::executeStep()
    {
        if (false == mbDone)
        {
            const int ret = sqlite3_step(mStmtPtr);
            if (SQLITE_ROW == ret) // one row is ready : call getColumn(N) to access it
            {
                mbOk = true;
            }
            else if (SQLITE_DONE == ret) // no (more) row ready : the query has finished executing
            {
                mbOk = false;
                mbDone = true;
            }
            else
            {
                mbOk = false;
                mbDone = false;
                throw SQLite::Exception(mStmtPtr, ret);
            }
        }
        else
        {
            throw SQLite::Exception("Statement needs to be reseted.");
        }

        return mbOk; // true only if one row is accessible by getColumn(N)
    }

// Execute a one-step query with no expected result
    int Statement::exec()
    {
        if (false == mbDone)
        {
            const int ret = sqlite3_step(mStmtPtr);
            if (SQLITE_DONE == ret) // the statement has finished executing successfully
            {
                mbOk = false;
                mbDone = true;
            }
            else if (SQLITE_ROW == ret)
            {
                mbOk = false;
                mbDone = false;
                throw SQLite::Exception("exec() does not expect results. Use executeStep.");
            }
            else
            {
                mbOk = false;
                mbDone = false;
                throw SQLite::Exception(mStmtPtr, ret);
            }
        }
        else
        {
            throw SQLite::Exception("Statement need to be reseted.");
        }

        // Return the number of rows modified by those SQL statements (INSERT, UPDATE or DELETE)
        return sqlite3_changes(mStmtPtr);
    }

// Return a copy of the column data specified by its index starting at 0
// (use the Column copy-constructor)
    Column Statement::getColumn(const int aIndex)
    {
        checkRow();
        checkIndex(aIndex);

        // Share the Statement Object handle with the new Column created
        return Column(mStmtPtr, aIndex);
    }

// Return a copy of the column data specified by its column name starting at 0
// (use the Column copy-constructor)
    Column  Statement::getColumn(const char* apName)
    {
        checkRow();
        const int index = getColumnIndex(apName);

        // Share the Statement Object handle with the new Column created
        return Column(mStmtPtr, index);
    }

// Test if the column is NULL
    bool Statement::isColumnNull(const int aIndex) const
    {
        checkRow();
        checkIndex(aIndex);
        return (SQLITE_NULL == sqlite3_column_type(mStmtPtr, aIndex));
    }

    bool Statement::isColumnNull(const char* apName) const
    {
        checkRow();
        const int index = getColumnIndex(apName);
        return (SQLITE_NULL == sqlite3_column_type(mStmtPtr, index));
    }

// Return the named assigned to the specified result column (potentially aliased)
    const char* Statement::getColumnName(const int aIndex) const
    {
        checkIndex(aIndex);
        return sqlite3_column_name(mStmtPtr, aIndex);
    }

#ifdef SQLITE_ENABLE_COLUMN_METADATA
    // Return the named assigned to the specified result column (potentially aliased)
const char* Statement::getColumnOriginName(const int aIndex) const
{
    checkIndex(aIndex);
    return sqlite3_column_origin_name(mStmtPtr, aIndex);
}
#endif

// Return the index of the specified (potentially aliased) column name
    int Statement::getColumnIndex(const char* apName) const
    {
        // Build the map of column index by name on first call
        if (mColumnNames.empty())
        {
            for (int i = 0; i < mColumnCount; ++i)
            {
                const char* pName = sqlite3_column_name(mStmtPtr, i);
                mColumnNames[pName] = i;
            }
        }

        const TColumnNames::const_iterator iIndex = mColumnNames.find(apName);
        if (iIndex == mColumnNames.end())
        {
            throw SQLite::Exception("Unknown column name.");
        }

        return (*iIndex).second;
    }

// Return the numeric result code for the most recent failed API call (if any).
    int Statement::getErrorCode() const noexcept // nothrow
    {
        return sqlite3_errcode(mStmtPtr);
    }
// Return the extended numeric result code for the most recent failed API call (if any).
    int Statement::getExtendedErrorCode() const noexcept // nothrow
    {
        return sqlite3_extended_errcode(mStmtPtr);
    }
// Return UTF-8 encoded English language explanation of the most recent failed API call (if any).
    const char* Statement::getErrorMsg() const noexcept // nothrow
    {
        return sqlite3_errmsg(mStmtPtr);
    }

////////////////////////////////////////////////////////////////////////////////
// Internal class : shared pointer to the sqlite3_stmt SQLite Statement Object
////////////////////////////////////////////////////////////////////////////////

/**
 * @brief Prepare the statement and initialize its reference counter
 *
 * @param[in] apSQLite  The sqlite3 database connexion
 * @param[in] aQuery    The SQL query string to prepare
 */
    Statement::Ptr::Ptr(sqlite3* apSQLite, std::string& aQuery) :
            mpSQLite(apSQLite),
            mpStmt(NULL),
            mpRefCount(NULL)
    {
        const int ret = sqlite3_prepare_v2(apSQLite, aQuery.c_str(), static_cast<int>(aQuery.size()), &mpStmt, NULL);
        if (SQLITE_OK != ret)
        {
            throw SQLite::Exception(apSQLite, ret);
        }
        // Initialize the reference counter of the sqlite3_stmt :
        // used to share the mStmtPtr between Statement and Column objects;
        // This is needed to enable Column objects to live longer than the Statement objet it refers to.
        mpRefCount = new unsigned int(1);  // NOLINT(readability/casting)
    }

/**
 * @brief Copy constructor increments the ref counter
 *
 * @param[in] aPtr Pointer to copy
 */
    Statement::Ptr::Ptr(const Statement::Ptr& aPtr) :
            mpSQLite(aPtr.mpSQLite),
            mpStmt(aPtr.mpStmt),
            mpRefCount(aPtr.mpRefCount)
    {
        assert(NULL != mpRefCount);
        assert(0 != *mpRefCount);

        // Increment the reference counter of the sqlite3_stmt,
        // asking not to finalize the sqlite3_stmt during the lifetime of the new objet
        ++(*mpRefCount);
    }

/**
 * @brief Decrement the ref counter and finalize the sqlite3_stmt when it reaches 0
 */
    Statement::Ptr::~Ptr() noexcept // nothrow
    {
        assert(NULL != mpRefCount);
        assert(0 != *mpRefCount);

        // Decrement and check the reference counter of the sqlite3_stmt
        --(*mpRefCount);
        if (0 == *mpRefCount)
        {
            // If count reaches zero, finalize the sqlite3_stmt, as no Statement nor Column objet use it anymore.
            // No need to check the return code, as it is the same as the last statement evaluation.
            sqlite3_finalize(mpStmt);

            // and delete the reference counter
            delete mpRefCount;
            mpRefCount = NULL;
            mpStmt = NULL;
        }
        // else, the finalization will be done later, by the last object
    }


}  // namespace SQLite
/**
 * @file    Transaction.cpp
 * @ingroup SQLiteCpp
 * @brief   A Transaction is way to group multiple SQL statements into an atomic secured operation.
 *
 * Copyright (c) 2012-2013 Sebastien Rombauts (sebastien.rombauts@gmail.com)
 *
 * Distributed under the MIT License (MIT) (See accompanying file LICENSE.txt
 * or copy at http://opensource.org/licenses/MIT)
 */



namespace SQLite
{


// Begins the SQLite transaction
    Transaction::Transaction(Database& aDatabase) :
            mDatabase(aDatabase),
            mbCommited(false)
    {
        mDatabase.exec("BEGIN");
    }

// Safely rollback the transaction if it has not been committed.
    Transaction::~Transaction() noexcept // nothrow
    {
        if (false == mbCommited)
        {
            try
            {
                mDatabase.exec("ROLLBACK");
            }
            catch (SQLite::Exception&)
            {
                // Never throw an exception in a destructor: error if already rollbacked, but no harm is caused by this.
            }
        }
    }

// Commit the transaction.
    void Transaction::commit()
    {
        if (false == mbCommited)
        {
            mDatabase.exec("COMMIT");
            mbCommited = true;
        }
        else
        {
            throw SQLite::Exception("Transaction already commited.");
        }
    }


}  // namespace SQLite

#endif // SQLITE_CPP_HEADER_
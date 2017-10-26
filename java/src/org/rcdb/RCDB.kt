@file:JvmName("RCDB")

package org.rcdb

/**
 * Creates CCDB data provider with connection string
 */
public fun createProvider(connectionStr: String): JDBCProvider {

    if (connectionStr.startsWith("sqlite://")) {

        //first lets check that sqlite string is right. The problem is that ccdb sticks to SqlAlchemy provider
        //where connection string for sqlite should start with sqlite:/// (three slashes)
        if (!connectionStr.startsWith("sqlite:///")) {
            throw IllegalArgumentException("Connection string for sqlite should start with 'sqlite:///' (3 slashes). " +
            "Provided connection string is'$connectionStr'")
        }
        return SQLiteProvider(connectionStr)
    }

    if (connectionStr.startsWith("mysql://")) {
        return MySqlProvider(connectionStr)
    }

    throw IllegalArgumentException("Can't open the connection string. Current version of CCDB Java opens only MySql " +
    "(should start with 'mysql://') and SQLite (should start with 'sqlite:///'). " +
    " Provided string: '$connectionStr'")
}
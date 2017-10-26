package org.rcdb

import java.sql.DriverManager
import java.sql.Connection

public class SQLiteProvider(connectionString:String): JDBCProvider(connectionString) {


    override fun connect()
    {
        //first check for uri type
        val typePos = connectionString.indexOf("sqlite:///")
        if(typePos != 0){
            throw IllegalArgumentException("Connection string doesn't start with sqlite:/// but is given to SQLiteProvider. (Notice 3 slashes ///)")
        }

        //ok we replace CCDB 'sqlite:///' to JDBC 'jdbc:sqlite:'
        val host = "jdbc:sqlite:" + connectionString.substring(10)

        //Connect to through JDBC
        connectJDBC(host)
    }

    private fun connectJDBC(host:String){
        // load the sqlite-JDBC driver using the current class loader
        Class.forName("org.sqlite.JDBC");


        connection = DriverManager.getConnection(host)

        val con:Connection = connection!!

        prsConditionType = con.prepareStatement("SELECT id, name, value_type FROM condition_types")
        prsCondition = con.prepareStatement("SELECT id, bool_value, float_value, int_value, text_value, time_value FROM conditions WHERE run_number = ? AND condition_type_id = ?")
        prsFileNames = con.prepareStatement("SELECT files.path AS files_path "
                                                + "FROM files, files_have_runs AS files_have_runs_1 "
                                                + "WHERE files.id = files_have_runs_1.files_id "
                                                + "AND ? = files_have_runs_1.run_number "
                                                + "ORDER BY files.id DESC")
        prsFile = con.prepareStatement("SELECT files.id AS files_id, "
                                           + "       files.path AS files_path, "
                                           + "       files.sha256 AS files_sha256, "
                                           + "       files.content AS files_content "
                                           + "FROM files, files_have_runs AS files_have_runs_1 "
                                           + "WHERE files.path = ? AND files.id = files_have_runs_1.files_id "
                                           + "      AND ? = files_have_runs_1.run_number "
                                           + "ORDER BY files.id DESC")
        postConnect()
    }
}

package org.rcdb

import java.sql.DriverManager
import java.sql.Connection



public class MySqlProvider(connectionString: String) : JDBCProvider(connectionString) {

    override fun connect() {
        // load the sqlite-JDBC driver using the current class loader
        Class.forName("com.mysql.jdbc.Driver");

        //first check for uri type
        val typePos = connectionString.indexOf("mysql://")
        if (typePos != 0) {
            throw IllegalArgumentException("Connection string doesn't start with mysql:// but is given to MySqlProvider")
        }

        //ok we don't need mysql:// in the future. Moreover it will mess our separation logic
        var workStr = connectionString.substring(8)
        var userName = "rcdb"
        var password = ""

        //then if there is '@' that separates login/password part of uri
        val atPos = workStr.indexOf('@')

        if (atPos != -1) {
            var logPassStr: String
            when (atPos) {
                (workStr.length - 1) -> {
                    //it is like 'login:pwd@' string
                    logPassStr = workStr.substring(0, atPos)
                    workStr = ""
                }
                0 -> {
                    //it is like '@localhost' string
                    workStr = workStr.substring(1)
                    logPassStr = ""
                }
                else -> {
                    //a regular case
                    logPassStr = workStr.substring(0, atPos);
                    workStr = workStr.substring(atPos + 1);
                }
            }

            //is it only login or login&&password?
            var colonPos = logPassStr.indexOf(':');
            if (colonPos != -1) {
                userName = logPassStr.substring(0, colonPos)
                password = logPassStr.substring(colonPos + 1)
            } else {
                userName = logPassStr
            }
        }

        //ok, now we have only "address:port/database" part of the string
        //if we doesn't have /<database> we have to add it
        val host = "jdbc:mysql://" +
                if (workStr.indexOf('/') == -1) workStr + "/rcdb" else workStr

        //Connect to through JDBC
        connectJDBC(host, userName, password)
    }

    private fun connectJDBC(host: String, userName: String, password: String) {
        connection = DriverManager.getConnection(host, userName, password)

        val con: Connection = connection!!

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
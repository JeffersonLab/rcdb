import rcdb.web

# Set the SQL connection string (edit as necessary)
rcdb.web.app.config["SQL_CONNECTION_STRING"] = "mysql://rcdb@hallddb.jlab.org/rcdb2"

application = rcdb.web.app

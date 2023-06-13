RCDB have a logging system which stores some information about what is going on in the same database in *'log_records'*
table.


Set '''RCDB_USER''' environment variable to have your name in logs (or set it manually in API as shown below)


* Creating condition types goes to log automatically
* All condition values manipulations are not logged

It is done in assumption, that the database has many runs and each run has many condition values,
so if each condition value creation will have text log message, the database will be bloated with log records.


From the other point of view, when you do a series of operations with conditions it may be a good idea to left a
log message that could be seen by other users.


Custom data modification by SQLAlchemy, like creating or deleting objects manually with session.commit() is not
logged too, so log notification is left to user here too.


How to left a log record:

<syntaxhighlight lang="python">
# set RCDB_USER environment variable to give RCDB you user name
# another option is to give it in constructor
db = RCDBProvider("sqlite:///example.db", user_name="john")

# and one more option of setting user name
db.user_name = "john"

# simplest log version
db.add_log_record(None, "Hello everybody! You'll see this message in logs on RCDB site", 0)
</syntaxhighlight>

First None means there is no specific database object ID for this message. The last '0' means there is no specific run number for this message

=Common errors=

===== OperationalError: (OperationalError) unable to open database file None None =====
short: db file permissions
long:
For sqlite server it usually means that something is wrong with file 
permissions for sqlite database. Try to review permissions chown or chmod the file


===== SyntaxError: invalid syntax =====
short: python version
long: 
The error usually looks like this

lorentz:marki:rcdb> python start_www.py
Traceback (most recent call last):
  File "start_www.py", line 20, in <module>
  ...
  File "/home/marki/p12/rcdb/rcdb/python/rcdb/model.py", line 266
    rbt = {record.key: record for record in self.records}
                                ^
SyntaxError: invalid syntax

If python complaining about syntax it usually means that the python 
is of the older version (2.4, 2.6). RCDB works with python 2.7
                                



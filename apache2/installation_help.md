==RCDB apache installation==
It is considered that to run RCDB for Apache2 mod_wsgi is used. 

To install it on debian machine:
apt-get install libapache2-mod-wsgi

In general, to run application with mod_wsgi and apache one needs
two files:
1. Apache site config file
2. .wsgi file. This file contains the code mod_wsgi is executing on 
startup to get the application to run. 

=== wsgi file ==
.wsgi file to run RCDB is located in 
$RCDB_HOME/rcdb/rcdb_www/rcdb.wsgi

There is no need to edit the file. Everything is done automatically there


=== Apache2 configuration ===
sample configuration file for the apache2 is in 
$RCDB_HOME/rcdb/apache2/rcdb.conf

To install it one needs to:
1. Copy file to /etc/apache2/sites-avalable
2. ln -s /etc/apache2/sites-avalable/rcdb.conf /etc/apache2/sites-enabled
3. edit /etc/apache2/sites-avalable/rcdb.conf,
   change all /home/romanov links to where RCDB is located
   set RCDB_CONNECTION string to your database
4. restart apache
5. application should run on 127.0.0.1

=== Advanced configuration ===
RCDB uses FLASK framework to render the site

General information about using flask with mod_wsgi + apache could be found here
http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/



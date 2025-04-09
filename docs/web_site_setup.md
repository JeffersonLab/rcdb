# Installing RCDB Website

Here RHEL9 + Apache Server + mod_wsgi is considered as this setup is mainly used at Jefferson Lab. 


## Prerequisites

- RHEL9 server with Apache HTTP Server installed
- Root access or sudo privileges
- Python 3.9+ (default on RHEL9)
- `mod_wsgi` package for Apache

## 1. Install Required Packages

First, install the necessary packages:

```bash
# Install Apache and mod_wsgi
sudo dnf install httpd python3-mod_wsgi

# Install required Python packages
sudo dnf install python3-pip python3-devel

# Start and enable Apache
sudo systemctl enable --now httpd
```

## 2. Install RCDB Library

You have two options for installing the RCDB library:

### Option A: System-wide Installation

```bash
sudo pip3 install rcdb
```

### Option B: Virtual Environment (Recommended)

```bash
# Create a virtual environment, activate, install rcdb, exit
python3 -m venv /opt/venvs/rcdb
source /opt/venvs/rcdb/bin/activate
pip install rcdb
deactivate
```

## 3. Create the WSGI Script

Create a WSGI script at `/group/halld/www/halldwebdev/html/rcdb/rcdb_www.wsgi`:

If RCDB is installed as a system-wide library: 

```python
# OPTION A: For system-wide installation
import rcdb.web

# Connection string - adjust as needed
rcdb.web.app.config["SQL_CONNECTION_STRING"] = "mysql://rcdb@hallddb.jlab.org/rcdb2"

# 'application' is what mod_wsgi looks for
application = rcdb.web.app
```

If venv is used library:

```python
import sys
import os

# Add where to look for RCDB
venv_path = '/opt/venvs/rcdb/'
site_packages = os.path.join(venv_path, 'lib', 'python3.9', 'site-packages')
sys.path.insert(0, site_packages)

# Import and configure the RCDB web application
import rcdb.web

# Default connection string - adjust as needed
rcdb.web.app.config["SQL_CONNECTION_STRING"] = "mysql://rcdb@hallddb.jlab.org/rcdb2"

# This is what mod_wsgi looks for
application = rcdb.web.app
```

## 4. Configure Apache

Create an Apache configuration file at `/etc/httpd/conf.d/rcdb.conf`:

```apache
<VirtualHost *:80>
    # If you want to serve the app at a specific host
    # ServerName rcdb.example.com
    
    # Mount the RCDB web interface at /rcdb
    WSGIScriptAlias /rcdb /group/halld/www/halldwebdev/html/rcdb/rcdb_www.wsgi
    
    # Set the database connection string
    SetEnv RCDB_CONNECTION "mysql://rcdb@hallddb.jlab.org/rcdb2"
    
    # If using a virtual environment, specify the python-home
    # Uncomment the line below if using Option B (virtual environment)
    # WSGIDaemonProcess rcdb_www python-home=/opt/venvs/rcdb/ threads=5
    
    # If using system-wide installation, use this instead
    WSGIDaemonProcess rcdb_www threads=5
    
    WSGIProcessGroup rcdb_www
    WSGIApplicationGroup %{GLOBAL}
    
    <Directory /group/halld/www/halldwebdev/html/rcdb>
        Require all granted
    </Directory>
</VirtualHost>
```


## 5. Restart Apache

```bash
sudo systemctl restart httpd
```

## Additional Notes

- The RCDB web interface requires the proper database schema to be installed
- For production use, consider setting up HTTPS with SSL certificates
- Consider adjusting the number of threads in the WSGIDaemonProcess directive based on your server's capacity and expected load

Now your RCDB web interface should be up and running on your RHEL9 Apache server!
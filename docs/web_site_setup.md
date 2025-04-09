# Installing RCDB Website

Instruction on how to install central RCDB website.  

We use RHEL9 + Apache Server + mod_wsgi as the example, as this is what usually is used at Jefferson Lab (now is 2025).

There is [a dockerfile with example Rocky Linux 9](https://github.com/JeffersonLab/rcdb/tree/main/docker/rocky) 
(binary compatible with RHEL9) setup with config files. To build and run it:

```bash
# Assuming cwd is rcdb repo root:
cd docker/rocky
docker build -t rcdb-rocky:latest .
docker run --rm -it --init -p 8888:80 rcdb-rocky:latest

# site should be seen on 
http://localhost:8888/rcdb/
```


- RHEL9 (or compatible) server with Apache HTTP Server installed
- Root access or sudo privileges
- Python 3.9+ (default on RHEL9)
- `mod_wsgi` package for Apache

## Install Required Packages

First, install the necessary packages:

```bash
# Install Apache and mod_wsgi
sudo dnf install httpd python3-mod_wsgi python3-pip python3-devel

# Start and enable Apache
sudo systemctl enable --now httpd
```

There are two ways of managing rcdb and dependencies: 

- Install centrally on the server e.g. via RPM
- Install venv and use mod_wsgi with python and packages from venv

Both have procs and cons. 
Using system-wide packages simplifies centralized updates across multiple RHEL servers; 
If you need specific package version and package isolation from system changes and 
e.g. when multiple sites on a server require different versions of the same packages, 
a dedicated Python virtual environment is preferable.

**If you choose the route A - use centrally installed RPMs**

```
# Enable EPEL and CRB
dnf install -y epel-release 
dnf config-manager --set-enabled epel
dnf config-manager --set-enabled crb

# Install rcdb dependendencies
dnf install -y \
  python3-markupsafe \
  python3-click \
  python3-rich \
  python3-sqlalchemy \
  python3-mako \
  python3-ply \
  python3-PyMySQL \
  python3-pygments \
  python3-flask
```


## Install RCDB Library

You have two options for installing the RCDB library:

### Option A: System-wide Installation

```bash
git clone --depth=1 https://github.com/JeffersonLab/rcdb.git /opt/rcdb

# Install RCDB *without* re-downloading dependencies (they are from RPM)
# The --no-deps flag ensures pip won’t try to reinstall them.
cd /opt/rcdb/python
python3 -m pip install --no-cache-dir --no-deps .
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
    
    # If WSGI script is using RCDB_CONNECTION environment variable (not in this example)    
    # Set the database connection string
    # SetEnv RCDB_CONNECTION "mysql://rcdb@hallddb.jlab.org/rcdb2"
    
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
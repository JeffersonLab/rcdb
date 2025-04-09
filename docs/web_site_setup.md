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
# Create a virtual environment
cd /group/halld/www/halldwebdev/html/rcdb
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install RCDB within the virtual environment
pip install rcdb

# Deactivate when you're done
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

# ===== CHOOSE ONE OF THE FOLLOWING OPTIONS =====

# OPTION A: For system-wide installation
# No additional path manipulation needed if RCDB is installed system-wide

# OPTION B: For virtual environment
venv_path = '/group/halld/www/halldwebdev/html/rcdb/venv'
site_packages = os.path.join(venv_path, 'lib', 'python3.9', 'site-packages')
sys.path.insert(0, site_packages)

# =====

# Import and configure the RCDB web application
import rcdb.web

# Set the database connection string
if "RCDB_CONNECTION" in os.environ:
    rcdb.web.app.config["SQL_CONNECTION_STRING"] = os.environ["RCDB_CONNECTION"]
else:
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
    # WSGIDaemonProcess rcdb_www python-home=/group/halld/www/halldwebdev/html/rcdb/venv threads=5
    
    # If using system-wide installation, use this instead
    WSGIDaemonProcess rcdb_www threads=5
    
    WSGIProcessGroup rcdb_www
    WSGIApplicationGroup %{GLOBAL}
    
    <Directory /group/halld/www/halldwebdev/html/rcdb>
        Require all granted
    </Directory>
</VirtualHost>
```

## 5. Set Permissions

Ensure Apache can access the RCDB files:

```bash
# Check ownership of the directory
ls -la /group/halld/www/halldwebdev/html/rcdb/

# Set appropriate permissions
sudo chown -R apache:apache /group/halld/www/halldwebdev/html/rcdb/
# OR add read permissions for others
sudo chmod -R o+r /group/halld/www/halldwebdev/html/rcdb/
sudo chmod o+x /group/halld/www/halldwebdev/html/rcdb/
```

## 6. Configure SELinux (if enabled)

If SELinux is enabled on your system:

```bash
# Allow Apache to connect to the database
sudo setsebool -P httpd_can_network_connect_db 1

# Set proper context for the WSGI file
sudo chcon -t httpd_sys_content_t /group/halld/www/halldwebdev/html/rcdb/rcdb_www.wsgi
```

## 7. Restart Apache

```bash
sudo systemctl restart httpd
```

## 8. Test the Installation

Visit `http://your-server/rcdb` in your web browser.

If you encounter issues, check the Apache error logs:

```bash
sudo tail -f /var/log/httpd/error_log
```

## Troubleshooting

### Missing Modules

If you encounter missing module errors, install them with pip:

```bash
# For system-wide installation
sudo pip3 install flask sqlalchemy pymysql

# For virtual environment
source /group/halld/www/halldwebdev/html/rcdb/venv/bin/activate
pip install flask sqlalchemy pymysql
deactivate
```

### Permissions Issues

If you see permission denied errors:

```bash
# Check SELinux status
sestatus

# If SELinux is enforcing, try setting it to permissive temporarily for testing
sudo setenforce 0

# After testing, remember to set it back to enforcing
sudo setenforce 1
```

### Database Connection Issues

If the website loads but database connection fails:

1. Verify your connection string in the Apache config and WSGI script
2. Check if the database server allows connections from your web server
3. Test the connection manually:

```bash
python3 -c "import pymysql; pymysql.connect(host='hallddb.jlab.org', user='rcdb', db='rcdb2')"
```

## Additional Notes

- The RCDB web interface requires the proper database schema to be installed
- For production use, consider setting up HTTPS with SSL certificates
- Consider adjusting the number of threads in the WSGIDaemonProcess directive based on your server's capacity and expected load

Now your RCDB web interface should be up and running on your RHEL9 Apache server!
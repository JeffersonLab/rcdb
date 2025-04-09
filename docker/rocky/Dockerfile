# docker build -t rcdb-rocky:latest .
# docker run --rm -it --init rcdb-rocky:latest
# docker run --rm -it --init -p8888:8888 rcdb-rocky:latest

# ----------------------------------------------------
# Dockerfile for running RCDB on Rocky Linux 9
# ----------------------------------------------------
FROM rockylinux:9

LABEL maintainer="Dmitry Romanov <romanov@jlab.org>"

# Enable EPEL and CRB
RUN dnf install -y epel-release && \
    dnf config-manager --set-enabled epel && \
    dnf config-manager --set-enabled crb


# Install system packages and rcdb dependendencies

RUN dnf install -y \
      httpd \
      git \
      # Python and RCDB deps \
      python3-devel \
      python3-pip \
      python3-mod_wsgi \
      python3-markupsafe \
      python3-click \
      python3-rich \
      python3-sqlalchemy \
      python3-mako \
      python3-ply \
      python3-PyMySQL \
      python3-pygments \
      python3-flask \
    && dnf clean all \
    && rm -rf /var/cache/yum

# ----------------------------------------------------
# Clone RCDB repo and install Python library
# ----------------------------------------------------
RUN git clone --depth=1 https://github.com/JeffersonLab/rcdb.git /opt/rcdb
WORKDIR /opt/rcdb/python

# Install RCDB *without* re-downloading dependencies (they are from RPM)
# The --no-deps flag ensures pip won’t try to reinstall them.
RUN pip3 install --no-cache-dir --no-deps .

# ----------------------------------------------------
# Set up Apache config & WSGI script
# ----------------------------------------------------
# Make sure the directory for your WSGI script matches httpd config
RUN mkdir -p /group/halld/www/halldwebdev/html/rcdb

# Copy WSGI script into place
COPY rcdb_www.wsgi /group/halld/www/halldwebdev/html/rcdb/rcdb_www.wsgi

# Copy Apache config to conf.d
COPY rcdb.conf /etc/httpd/conf.d/rcdb.conf

# ----------------------------------------------------
# Expose port 80 and run Apache in the foreground
# ----------------------------------------------------
EXPOSE 80

CMD ["/usr/sbin/httpd", "-D", "FOREGROUND"]

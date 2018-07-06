# Docker image for testing Ashlar -- installs pyenv, tox, and the OS-level
# dependencies needed to run Ashlar
FROM debian:jessie-slim

RUN apt-get update

# Install Python runtime dependencies
# Adapted from the official Python images:
# https://github.com/docker-library/python/blob/b8c94a31a98a535477200482a32c95192f85af5b/2.7/jessie/slim/Dockerfile#L12
RUN apt-get install -y  ca-certificates \
                        libgdbm3 \
                        libreadline6 \
                        libsqlite3-0 \
                        libssl1.0.0 \
                        netbase

# Install Python build dependencies
# Adapted from the official Python images:
# https://github.com/docker-library/python/blob/b8c94a31a98a535477200482a32c95192f85af5b/2.7/jessie/slim/Dockerfile#L27
Run apt-get install -y git \
                       dpkg-dev \
                       gcc \
                       libbz2-dev \
                       libc6-dev \
                       libdb-dev \
                       libgdbm-dev \
                       libncursesw5-dev \
                       libreadline-dev \
                       libsqlite3-dev \
                       libssl-dev \
                       make \
                       tcl-dev \
                       tk-dev \
                       wget \
                       xz-utils \
                       zlib1g-dev

# Install pyenv
RUN git clone git://github.com/yyuu/pyenv.git /.pyenv
ENV PYENV_ROOT /.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

# Install Python versions for testing
ENV PYVERSIONS "2.7.15 3.3.7 3.4.8 3.5.5 3.6.6"

RUN for pyversion in $PYVERSIONS; \
	do \
		pyenv install $pyversion; \
	done

RUN pyenv global 3.6.6
RUN pip install tox tox-pyenv

# Make Python versions available from the shell (e.g. $ python3.4)
RUN pyenv local $PYVERSIONS

# Install Ashlar OS-level dependencies
# Note that the version of GDAL installed in the OS is important -- Django 1.8
# is incompatible with GDAL 2.0+, which introduced 64-bit integers that can throw
# errors since Django is not prepared to handle them. The slim-jessie image
# will install GDAL 1.11, but if you change the base image you should
# double-check the version of GDAL that gets installed.
RUN apt-get -y autoremove && \
    apt-get install -y libgeos-dev \
                       binutils \
                       libproj-dev \
                       gdal-bin

COPY . /opt/ashlar
WORKDIR /opt/ashlar

# Run tox to test all Python versions
CMD ["tox"]

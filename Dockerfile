FROM python:2.7-slim-jessie

COPY . /opt/ashlar
WORKDIR /opt/ashlar

RUN apt-get update

# Note that the version of GDAL installed in the OS is important -- Django 1.8
# is incompatible with GDAL 2.0+, which introduced 64-bit integers that can throw
# errors since Django is not prepared to handle them. The slim-jessie image for
# Python 2.7 will install GDAL 1.11, but if you change the base image you should
# double-check the version of GDAL that gets installed.
RUN apt-get -y autoremove && \
    apt-get install -y libgeos-dev \
                       binutils \
                       libproj-dev \
                       gdal-bin

# --process-dependency-links is no longer a valid argument in pip 10. We should
# remove the external djsonb dependency eventually, but for now just install
# an earlier version of pip that can handle it.
RUN pip install pip==9.0.1

RUN pip install -U -r dev-requirements.txt
RUN pip install --process-dependency-links --allow-external djsonb -e .
CMD python run_tests.py

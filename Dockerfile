FROM python:2.7

COPY . /opt/ashlar
WORKDIR /opt/ashlar

RUN apt-get update
RUN apt-get -y autoremove && apt-get install -y libgeos-dev binutils libproj-dev gdal-bin

# Dependency links were removed in pip>6. We should remove the external djsonb
# dependency eventually, but for now just install an earlier version of pip that
# can handle it.
RUN pip install pip==6.0.7

RUN pip install --process-dependency-links --allow-external djsonb -e .
CMD python run_tests.py

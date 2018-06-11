FROM python:2.7

COPY . /opt/ashlar
WORKDIR /opt/ashlar

RUN apt-get update
RUN apt-get -y autoremove && apt-get install -y libgeos-dev binutils libproj-dev gdal-bin

# --process-dependency-links is no longer a valid argument in pip 10. We should
# remove the external djsonb dependency eventually, but for now just install
# an earlier version of pip that can handle it.
RUN pip install pip==9.0.1

RUN pip install --process-dependency-links --allow-external djsonb -e .
CMD python run_tests.py

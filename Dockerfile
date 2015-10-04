FROM python:2.7

COPY . /opt/ashlar
WORKDIR /opt/ashlar

RUN apt-get update
RUN apt-get -y autoremove && apt-get install -y libgeos-dev binutils libproj-dev gdal-bin

RUN pip install --process-dependency-links --allow-external djsonb -e .
CMD python run_tests.py

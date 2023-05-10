FROM continuumio/miniconda3

ARG user=trainer
ARG group=trainer
ARG uid=1000
ARG gid=1000
RUN mkdir /app
WORKDIR /app
COPY . .


RUN python3 -m pip install pipenv
RUN python3 -m pip install discord


RUN python -m pip install pymongo
RUN python -m pip install dnspython

RUN ln -s /opt/conda/lib/libcusolver.so.10 /opt/conda/lib/libcusolver.so.11



CMD ["python", "./main.py"]

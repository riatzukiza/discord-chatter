
FROM continuumio/miniconda3
 
ARG user=trainer
ARG group=trainer
ARG uid=1000
ARG gid=1000
# RUN  conda create --name tf-gpu python=3.9

# RUN  conda activate tf-gpu
RUN mkdir /app
WORKDIR /app
COPY . .

RUN python3 -m pip install discord


RUN python -m pip install pymongo[src]
RUN python -m pip install dnspython
RUN python -m pip install pillow


CMD ["python", "./main.py"]


FROM continuumio/miniconda3

# RUN  conda create --name tf-gpu python=3.9

# RUN  conda activate tf-gpu
RUN mkdir /app
WORKDIR /app
COPY . .

RUN python3 -m pip install discord


RUN python -m pip install pymongo[src]
RUN python -m pip install dnspython


CMD ["python", "./main.py"]

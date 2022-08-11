FROM continuumio/miniconda3

# RUN  conda create --name tf-gpu python=3.9

# RUN  conda activate tf-gpu
RUN mkdir /app
WORKDIR /app
COPY . .

RUN conda install -c conda-forge cudatoolkit=11.0 cudnn=8.2.1

RUN python3 -m pip install tensorflow-gpu
RUN python3 -m pip install discord
RUN python3 -m pip install sklearn


RUN python -m pip install pymongo
RUN python -m pip install dnspython
RUN python -m pip install pandas
RUN python -m pip install Django

RUN ln -s /opt/conda/lib/libcusolver.so.10 /opt/conda/lib/libcusolver.so.11



CMD ["python", "./main.py"]

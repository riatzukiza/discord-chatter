FROM continuumio/miniconda3

# RUN  conda create --name tf-gpu python=3.9

# RUN  conda activate tf-gpu
RUN mkdir /app
WORKDIR /app
COPY . .

RUN conda install -c conda-forge cudatoolkit=11.0 cudnn=8.2.1

RUN  python3 -m pip install tensorflow-gpu
RUN python3 -m pip install discord
RUN python3 -m pip install sklearn


CMD ["bash", "./start.sh"]
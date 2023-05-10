FROM tensorflow/tensorflow:2.12.0-gpu

RUN mkdir /app
WORKDIR /app
COPY . .

RUN python3 -m pip install discord
RUN python3 -m pip install scikit-learn
RUN python3 -m pip install tqdm

RUN python -m pip install pymongo
RUN python -m pip install dnspython

# RUN ln -s /opt/conda/lib/libcusolver.so.10 /opt/conda/lib/libcusolver.so.11

CMD ["python", "./main.py"]

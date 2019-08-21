FROM tiangolo/uvicorn-gunicorn:python3.7
LABEL maintainer="Sebastian Ramirez <tiangolo@gmail.com>"

# TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install

RUN rm -R ta-lib ta-lib-0.4.0-src.tar.gz


RUN pip install fastapi
RUN pip install numpy
RUN pip install scipy
COPY ./app_doc /app
WORKDIR /app
RUN pip install -r requirements.txt --upgrade
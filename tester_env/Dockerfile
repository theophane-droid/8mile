FROM python:3.8

COPY ./requirements.txt requirements.txt

RUN apt -y install wget tar

RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
RUN tar -xzf ta-lib-0.4.0-src.tar.gz
RUN cd ta-lib/ && ./configure --prefix=/usr && make && make install

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

WORKDIR /app

CMD python3 /app/test_dataprovider.py
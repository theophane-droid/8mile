FROM python:3.8

COPY ./requirements.txt requirements.txt

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

WORKDIR /app

CMD python3 /app/test_dataprovider.py
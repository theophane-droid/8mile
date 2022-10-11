from locale import normalize
from logging.handlers import DatagramHandler
import pandas as pd
import yfinance as yf
import time

from random import randint
from datetime import datetime
from elasticsearch import Elasticsearch
import pickle
from datetime import timedelta

import numpy as np
import torch

from abc import ABC, abstractmethod


yahoointervalconverter = {
    'minute': '1m',
    'hour': '1h',
    'day': '1d'
}

# TODO: add format checker for pair, interval, start, end

class DataProvider(ABC):
    """
    Provide an abstraction layer on the way to get data from a source
    """
    @abstractmethod
    def getData(self) -> pd.DataFrame:
        """
        Return a pandas dataframe with the data.
        The main columns are named be open, high, low, close, volume. In index is the date.
        """
        raise NotImplementedError()

class YahooDataProvider(DataProvider):
    """
    Get data from Yahoo Finance
    """

    def __init__(self,
            pair,
            start_date,
            end_date,
            interval='hour') -> None:
        """Initialize a YahooDataProvider

        Args:
            pair (str): exemple BTCUSD
            start_date (datetime.datetime): First date to get. Format : YYYY-MM-DD
            end_date (datetime.datetime): Last date to get. Format : YYYY-MM-DD
            interval (str, optional): Can be day, hour, or minute.
        """
        self.pair = pair
        self.start_date = start_date
        # add one interval to the end depending on the interval
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        if interval == 'day':
            self.end_date = end_date + timedelta(days=1)
        elif interval == 'hour':
            self.end_date = end_date + timedelta(hours=1)
        elif interval == 'minute':
            self.end_date = end_date + timedelta(minutes=1)
        else:
            raise ValueError('Interval must be day, hour or minute')
        self.interval = interval

    def getData(self) -> pd.DataFrame :
        """Returns a pandas dataframe with the data.

        Returns:
            pd.DataFrame: _description_
        """        
        # convert interval into yahoo format
        yinterval = yahoointervalconverter[self.interval]
        # convert pair into yahoo format
        ypair = f'{self.pair[:3]}-{self.pair[3:]}'

        data = yf.Ticker(ypair)
        data = data.history(start=self.start_date,
                            end=self.end_date, interval=yinterval)
        try:
            del data["Dividends"]
        except:
            pass
        try:
            del data["Stock Splits"]
        except:
            pass
        try:
            del data['Time']
        except:
            pass
        data.rename(columns={
            'Open': 'open', 
            'High': 'high', 
            'Low': 'low', 
            'Close': 'close', 
            'Volume': 'volume'
            }, inplace=True)
        return data

class CSVDataProvider(DataProvider):
    """
    Get data from CSV file. The file name must be in the format {pair}-{interval}.csv
    """

    def __init__(self,
        pair,
        start_date,
        end_date,
        directory,
        interval='hour'):
        """Initialize a CSVDataProvider

        Args:
            pair (str): exemple BTCUSD
            start_date (datetime.datetime): First date to get. Format : YYYY-MM-DD.
            end_date (datetime.datetime): Last date to get. Format : YYYY-MM-DD.
            interval (str, optional): Can be day, hour, or minute.
        """
        self.pair = pair
        self.start_date = start_date
        self.end_date = end_date
        self.directory = directory
        self.interval = interval

    def getData(self) -> pd.DataFrame:
        """Returns a pandas dataframe with the data.
        """
        data = pd.read_csv(f'{self.directory}/f-{self.pair.lower()}-{self.interval}.csv')
        df =data.rename(columns={'Open': 'open', 
                                'High': 'high', 
                                'Low': 'low', 
                                'Close': 'close', 
                                'Volume': 'volume'})
        df.index = pd.to_datetime(df['Unnamed: 0'])
        df.drop(columns=['Unnamed: 0'], inplace=True)
        df = df[np.logical_and(df.index >= self.start_date, df.index <= self.end_date)]
        return df


class ElasticDataProvider:
    """Get data from Elasticsearch. Index name must be in the format f-{pair}-{interval}.
       Main columns must be open, high, low, close, volume. And the date must be in the field @timestamp. 
    """
    def __init__(self,
            pair,
            start_date,
            end_date,
            es_url,
            es_user,
            es_pass,
            interval='hour') -> None:
        """Initialize a ElasticsearchDataprovider

        Args:
            pair (str): exemple BTCUSD
            start_date (datetime.datetime): First date to get. Format : YYYY-MM-DD.
            end_date (datetime.datetime): Last date to get. Format : YYYY-MM-DD.
            es_url (str): url of the elasticsearch server, example : https://localhost:9200
            es_user (str): name of the user for elasticsearch connection
            es_pass (str): password of the user for elasticsearch connection
            interval (str, optional): Can be day, hour, or minute.
        """
        self.pair = pair
        self.start_date = start_date
        self.end_date = end_date
        self.es_url = es_url
        self.es_user = es_user
        self.es_pass = es_pass
        self.interval = interval

    def connect(self):
        return Elasticsearch(
            self.es_url,
            http_compress=True,
            verify_certs=False,
            http_auth=(self.es_user, self.es_pass),
        )

    def download(self, from_, to, index_name):
        es = self.connect()
        query = {
            "query": {
                "bool" :{
                    "must" : {
                        "range": {
                            "@timestamp": {
                                "gte": from_,
                                "lte": to
                            }
                        }
                    }
                }
            }
        }
        result = es.search(index=index_name, body=query, size=10000)['hits']['hits']
        result = [x['_source'] for x in result]
        return result
    
    def download_data(self, pair, interval, from_, to):
        index_name = f'f-{pair.lower()}_{interval}'
        step = {
            'minute': timedelta(minutes=1),
            'hour' : timedelta(hours=1),
            'day' : timedelta(days=1),
            'week' : timedelta(weeks=1),
            'month' : timedelta(weeks=4),
        }
        beg = from_
        end = to
        end = to + step[interval] * 10000
        if end > to:
            end = to
        data = []
        while beg < to:

            data += self.download(beg, beg + step[interval] * 10000 if beg + step[interval] * 10000 < to else to, index_name)
            beg += step[interval] * 10000
            end += step[interval] * 10000
        data = pd.DataFrame(data)
        data.dropna(axis=1)
        return data
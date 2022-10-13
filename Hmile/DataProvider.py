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

from Hmile.Exception import DataframeFormatException, DataProviderArgumentException
from Hmile.FillPolicy import FillPolicyError

yahoointervalconverter = {
    'minute': '1m',
    'hour': '1h',
    'day': '1d'
}
interval_to_timedelta = {
    'minute' : timedelta(minutes=1),
    'hour' : timedelta(hours=1),
    'day' : timedelta(days=1)
}

class DataProvider(ABC):
    """
    Provide an abstraction layer on the way to get data from a source
    """
    def __init__(self, pair, interval, start, end) -> None:
        """Inialize a DataProvider

        Args:
            pair (str): the pair to get ex : BTCUSD
            interval (str): should be like day, hour or minute
            start (str): should be like 2020-12-31
            end (str): should be > start

        Raises:
            DataframeFormatException: When the dataframe does not correspond to Hmile norm
            DataProviderArgumentException: When the argument are not correct
        """
        self.checkArguments(pair, interval, start, end)
        self.pair = pair
        self.interval = interval
        self.start_date = start
        self.end_date = end
        self.fill_policy = FillPolicyError(self.interval)

    @abstractmethod
    def getData(self) -> pd.DataFrame:
        """
        Return a pandas dataframe with the data.
        The main columns are named be open, high, low, close, volume. In index is the date.
        The index name should be 'date'
        """
        raise NotImplementedError()
    
    def checkDataframe(self, dataframe):
        """Check if first columns in the dataframes are open, high, low, close, volume. 
        Check if index is a date and if the interval is the same between all rows"""
        columns = dataframe.columns
        if not columns[0] == 'open' or not columns[1] == 'high' or not columns[2] == 'low' or not columns[3] == 'close' or not columns[4] == 'volume':
            raise DataframeFormatException('The first columns in the dataframe should be open, high, low, close, volume', dataframe)
        if not isinstance(dataframe.index, pd.DatetimeIndex):
            raise DataframeFormatException('The index of the dataframe should be a date', dataframe)
        if not dataframe.index.is_monotonic_increasing:
            raise DataframeFormatException('The index of the dataframe should be monotonic increasing', dataframe)
        if not dataframe.index.is_unique:
            raise DataframeFormatException('The index of the dataframe should be unique', dataframe)
        if not dataframe.index.inferred_freq:
            self.fill_policy(dataframe)
            # TODO : use fill policy
        if dataframe.index.name != 'date':
            raise DataframeFormatException('The index name should be date', dataframe)
    
    def normalizeColumnsOrder(self, dataframe):
        """Normalize the order of the columns to open, high, low, close, volume. Sort others columns by alphabetical order
        
        Args:
            dataframe (pd.DataFrame): The dataframe to treat


        Returns:
            pd.DataFrame: After traitement
        """
        ohlcv = ['open', 'high', 'low', 'close', 'volume']
        others_col = [col for col in dataframe.columns if col not in ohlcv]
        others_col.sort()
        col_list = ohlcv + others_col
        return dataframe.reindex(columns=col_list)
    

    def checkArguments(self, pair, interval, start, end):
        """Check if the arguments are valid. pair should be like BTCUSD, interval should be in yahoointervalconverter, start and end should be like YYYY-MM-DD
        start should be before end. Length must be at least 3 interval.
        
        Args:
            pair (str): The pair to get
            interval (str): The interval of the data
            start (str): The start date
            end (str) The end date
        """
        if not pair:
            raise DataProviderArgumentException('pair should not be empty')
        if not interval:
            raise DataProviderArgumentException('interval should not be empty')
        if interval not in yahoointervalconverter.keys():
            print(interval)
            raise DataProviderArgumentException('interval should be in day, hour or minute')
        if not start:
            raise DataProviderArgumentException('start should not be empty')
        if not end:
            raise DataProviderArgumentException('end should not be empty')
        if not interval in yahoointervalconverter:
            raise DataProviderArgumentException('interval should be in ' + str(yahoointervalconverter))
        try:
            datetime.strptime(start, '%Y-%m-%d')
        except ValueError:
            raise DataProviderArgumentException('start should be like YYYY-MM-DD')
        try:
            datetime.strptime(end, '%Y-%m-%d')
        except ValueError:
            raise DataProviderArgumentException('end should be like YYYY-MM-DD')
        if datetime.strptime(start, '%Y-%m-%d') > datetime.strptime(end, '%Y-%m-%d'):
            raise DataProviderArgumentException('start should be before end')
        # check if length is at least 3 interval
        min_diff = interval_to_timedelta[interval] * 2
        diff = datetime.strptime(end, '%Y-%m-%d') - datetime.strptime(start, '%Y-%m-%d')
        if diff < min_diff:
            raise DataProviderArgumentException('Length must be at least 3 interval')
    
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
        super().__init__(pair, interval, start_date, end_date)
        self.pair = pair
        # add one interval to the end depending on the interval
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        # if interval == 'day':
        #     self.end_date = end_date + timedelta(days=1)
        # elif interval == 'hour':
        #     self.end_date = end_date + timedelta(hours=1)
        # elif interval == 'minute':
        #     self.end_date = end_date + timedelta(minutes=1)
        # else:
        #     raise ValueError('Interval must be day, hour or minute')

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
        data['date'] = data.index
        data.index = data['date']
        data.drop(columns=['date'], inplace=True)
        data = self.normalizeColumnsOrder(data)
        self.checkDataframe(data)
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
        super().__init__(pair, interval, start_date, end_date)
        self.directory = directory

    def getData(self) -> pd.DataFrame:
        """Returns a pandas dataframe with the data.
        """
        data = pd.read_csv(f'{self.directory}/f-{self.pair.lower()}-{self.interval}.csv')
        df =data.rename(columns={'Open': 'open', 
                                'High': 'high', 
                                'Low': 'low', 
                                'Close': 'close', 
                                'Volume': 'volume'})
        df.rename({'Unnamed: 0': 'date'}, axis=1, inplace=True)
        df.index = pd.to_datetime(df['date'])
        df.drop(columns=['date'], inplace=True)
        df = df[np.logical_and(df.index >= self.start_date, df.index <= self.end_date)]
        df = self.normalizeColumnsOrder(df)
        self.checkDataframe(df)
        return df


class ElasticDataProvider(DataProvider):
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
        super().__init__(pair, interval, start_date, end_date)
        self.es_url = es_url
        self.es_user = es_user
        self.es_pass = es_pass

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
        data.rename({'@timestamp': 'date'}, axis=1, inplace=True)
        return data

    def getData(self):
        start = datetime.strptime(self.start_date, '%Y-%m-%d')
        end = datetime.strptime(self.end_date, '%Y-%m-%d')
        data = self.download_data(self.pair, self.interval, start, end)
        data.index = pd.to_datetime(data['date'])
        data.drop(columns=['date'], inplace=True)
        data = self.normalizeColumnsOrder(data)
        self.checkDataframe(data)
        return data
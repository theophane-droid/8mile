import os
from logging.handlers import DatagramHandler
import pandas as pd
import yfinance as yf
import requests as r
from datetime import datetime
from elasticsearch import Elasticsearch
from datetime import timedelta
from typing import List, Dict

import numpy as np

from abc import ABC, abstractmethod

from Hmile.Exception import (DataframeFormatException,
                             DataProviderArgumentException,
                             DataNotAvailableException)
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
    
    :ivar pairs: list of the pairs to get ex : ['BTCUSD', 'ETHUSD']
    :ivar interval: day, hour or minute
    :ivar start: date of the first data to get
    :ivar end: date of the last data to get
    """
    def __init__(
        self,
        pairs : List[str],
        interval : str,
        start : str,
        end : str) -> None:
        """Inialize a DataProvider

        Args:
            pairs (list): list of the pairs to get ex : ['BTCUSD', 'ETHUSD']
            interval (str): should be like day, hour or minute
            start (str): should be like 2020-12-31
            end (str): should be > start

        Raises:
            DataframeFormatException: When the dataframe does not correspond to Hmile norm
            DataProviderArgumentException: When the argument are not correct
        """
        self.checkArguments(pairs, interval, start, end)
        self.pairs = pairs
        self.interval = interval
        self.start_date = start
        self.end_date = end
        self.fill_policy = FillPolicyError(self.interval)

    def getData(self) -> Dict[str, pd.DataFrame]:
        """
        Return a dict of dataframes with the key the pair and the value the corresponding dataframe.
        Every dataframe should have the same columns and the same index : 
        The main columns are named be open, high, low, close, volume. In index is the date.
        The index name is'date'
        
        Returns:
            Dict[str, pd.DataFrame]: The dict of dataframes
        """
        result = {}
        for pair in self.pairs:
            try:
                dataframe = self._getOnePair(pair)
            except Exception as e:
                # we first check if the exception is not a Hmile exception
                if isinstance(e, NotImplementedError):
                    raise e
                raise DataNotAvailableException(pair, self.start_date, self.end_date)
            # if len dataframe == 0 we raise an exception
            if dataframe.shape[0] == 0:
                raise DataNotAvailableException(pair, self.start_date, self.end_date)
            # we check the dataframe
            self.checkDataframe(dataframe)
            result[pair] = dataframe
        return result
       
    @abstractmethod
    def _getOnePair(self, pair_name) -> pd.DataFrame:
        """Return the dataframe of the pair. This method should be implemented by the child class

        Raises:
            NotImplementedError: _description_

        Returns:
            pd.DataFrame: the dataframe of the pair between self.start_date and self.end_date with an interval of self.interval
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
    

    def checkArguments(
        self,
        pairs : List[str],
        interval : str,
        start : str,
        end : str) -> None:
        """Check if the arguments are valid. pair should be like BTCUSD, interval should be in yahoointervalconverter, start and end should be like YYYY-MM-DD
        start should be before end. Length must be at least 3 interval.
        
        Args:
            pairs (List[str]): list of pairs to get
            interval (str): The interval of the data
            start (str): The start date
            end (str) The end date
            
        Raises:
            DataProviderArgumentException: When the arguments are not correct
        """
        if not pairs:
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
        
    def getAvailablePairs(self) -> List[str]:
        """Return the list of available pairs

        Raises:
            NotImplementedError: if the current dataprovider does not implement this method

        Returns:
            List[str]: the list of available pairs
        """
        raise NotImplementedError(f'{self.__class__.__name__} does not implement getAvailablePairs()')
    
class YahooDataProvider(DataProvider):
    """
    Get data from Yahoo Finance
    
    :ivar pairs: list of pairs to get
    :ivar interval: The interval of the data
    :ivar start_date: The start date
    :ivar end_date: The end date
    :ivar fill_policy: The fill policy to use
    """

    def __init__(self,
            pairs : List[str],
            start_date : str,
            end_date : str,
            interval : str = 'hour') -> None:
        """Initialize a YahooDataProvider

        Args:
            pairs (list): list of the pairs to get ex : ['BTCUSD', 'ETHUSD']
            start_date (datetime.datetime): First date to get. Format : YYYY-MM-DD
            end_date (datetime.datetime): Last date to get. Format : YYYY-MM-DD
            interval (str, optional): Can be day, hour, or minute.
        """
        super().__init__(pairs, interval, start_date, end_date)

    def _getOnePair(self, pair) -> pd.DataFrame :        
        # convert interval into yahoo format
        yinterval = yahoointervalconverter[self.interval]
        # convert pair into yahoo format
        ypair = f'{pair[:3]}-{pair[3:]}'

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
        return data

class CSVDataProvider(DataProvider):
    """
    Get data from CSV file. The file name must be in the format f-{pair}-{interval}.csv
    
    :ivar pairs: list of pairs to get
    :ivar interval: The interval of the data
    :ivar start_date: The start date
    :ivar end_date: The end date
    :ivar fill_policy: The fill policy to use
    :ivar directory: The directory where the csv files are
    """

    def __init__(self,
        pairs : List[str],
        start_date : str,
        end_date : str,
        directory : str,
        interval : str = 'hour'):
        """Initialize a CSVDataProvider

        Args:
            pairs (List[str]): list of the pairs to get ex : ['BTCUSD', 'ETHUSD']
            start_date (datetime.datetime): First date to get. Format : YYYY-MM-DD.
            end_date (datetime.datetime): Last date to get. Format : YYYY-MM-DD.
            interval (str, optional): Can be day, hour, or minute.
        """
        super().__init__(pairs, interval, start_date, end_date)
        self.directory = directory

    def _getOnePair(self, pair) -> pd.DataFrame:
        data = pd.read_csv(f'{self.directory}/f-{pair.lower()}-{self.interval}.csv')
        df = data.rename(columns={'Open': 'open', 
                                'High': 'high', 
                                'Low': 'low', 
                                'Close': 'close', 
                                'Volume': 'volume'})
        df.rename({'Unnamed: 0': 'date'}, axis=1, inplace=True)
        df.index = pd.to_datetime(df['date'])
        df.drop(columns=['date'], inplace=True)
        df = df[np.logical_and(df.index >= self.start_date, df.index <= self.end_date)]
        df = self.normalizeColumnsOrder(df)
        return df

    def getAvailablePairs(self) -> List[str]:
        """Return the list of available pairs

        Returns:
            List[str]: the list of available pairs
        """
        files = os.listdir(self.directory)
        pairs = []
        for f in files:
            if f.startswith('f-') and f.endswith(f'-{self.interval}.csv'):
                pair = f[2:-len(f'-{self.interval}.csv')]
                pairs.append(pair.upper())
        pairs.sort()
        return pairs


class ElasticDataProvider(DataProvider):
    """
    Get data from Elasticsearch. Index name must be in the format f-{pair}-{interval}.
    Main columns must be open, high, low, close, volume. And the date must be in the field @timestamp. 
    
    :ivar pairs: list of pairs to get
    :ivar interval: The interval of the data
    :ivar start_date: The start date
    :ivar end_date: The end date
    :ivar fill_policy: The fill policy to use
    :ivar es_url: The url of the elasticsearch server
    :ivar es_user: The elasticsearch user to connect to
    :ivar es_pass: The elasticsearch password to connect to
    """
    def __init__(self,
            pairs : List[str],
            start_date : str,
            end_date : str,
            es_url : str,
            es_user : str,
            es_pass : str,
            interval : str = 'hour') -> None:
        """Initialize a ElasticsearchDataprovider

        Args:
            pairs (List[str]): exemple BTCUSD
            start_date (datetime.datetime): First date to get. Format : YYYY-MM-DD.
            end_date (datetime.datetime): Last date to get. Format : YYYY-MM-DD.
            es_url (str): url of the elasticsearch server, example : https://localhost:9200
            es_user (str): name of the user for elasticsearch connection
            es_pass (str): password of the user for elasticsearch connection
            interval (str, optional): Can be day, hour, or minute.
        """
        super().__init__(pairs, interval, start_date, end_date)
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

    def __download(self, from_, to, index_name):
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
    
    def __download_data(self, pair, interval, from_, to):
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

            data += self.__download(beg, beg + step[interval] * 10000 if beg + step[interval] * 10000 < to else to, index_name)
            beg += step[interval] * 10000
            end += step[interval] * 10000
        data = pd.DataFrame(data)
        data.dropna(axis=1)
        data.rename({'@timestamp': 'date'}, axis=1, inplace=True)
        return data

    def _getOnePair(self, pair) -> pd.DataFrame:
        start = datetime.strptime(self.start_date, '%Y-%m-%d')
        end = datetime.strptime(self.end_date, '%Y-%m-%d')
        data = self.__download_data(pair, self.interval, start, end)
        data.index = pd.to_datetime(data['date'])
        data.drop(columns=['date'], inplace=True)
        data = self.normalizeColumnsOrder(data)
        return data

    def getAvailablePairs(self) -> List[str]:
        """Return the list of available pairs

        Returns:
            List[str]: the list of available pairs
        """
        es = self.connect()
        indices = es.cat.indices(h='index', s='index').split()
        pairs = []
        for index in indices:
            if index.startswith('f-') and index.endswith(f'_{self.interval}'):
                pair = index[2:-len(f'_{self.interval}')]
                pairs.append(pair.upper())
        pairs.sort()
        return pairs

class PolygonDataProvider(DataProvider):
    """
    Download financial data from polygon.io
    
    :ivar pairs: list of pairs to get
    :ivar interval: The interval of the data
    :ivar start_date: The start date
    :ivar end_date: The end date
    :ivar fill_policy: The fill policy to use
    :ivar key: The polygon api key to use
    """
    def __init__(self, 
            pairs : List[str],
            start_date : str,
            end_date : str,
            api_key : str,
            interval : str = 'hour'):
        """Create a PolygonDataProvider

        Args:
            pairs (List[str]): exemple BTCUSD
            start_date (datetime.datetime): First date to get. Format : YYYY-MM-DD.
            end_date (datetime.datetime): Last date to get. Format : YYYY-MM-DD.
            api_key (str): api key for polygon.io
            interval (str, optional): Can be day, hour, or minute.
        """
        super().__init__(pairs, interval, start_date, end_date)
        self.api_key = api_key
        
    def __download(self, pair, interval, start, end):
        url = f'https://api.polygon.io/v2/aggs/ticker/X:{pair}/range/1/{interval}/{start}/{end}?adjusted=true&sort=asc&limit=50000&apiKey=8RvtCtdRW2bFH8WBE9JoihuwmnFECybm'
        json = r.get(url).json()
        return json['results']
        
    def _getOnePair(self, pair) -> pd.DataFrame:
        data = []
        last_datetime = datetime.strptime(self.start_date, '%Y-%m-%d')
        end = datetime.strptime(self.end_date, '%Y-%m-%d')
        while last_datetime < end:
            start_timestamp = int(last_datetime.timestamp() * 1000)
            end_timestamp = int((end).timestamp() * 1000)
            current_data = self.__download(pair, self.interval, start_timestamp, end_timestamp)
            data += current_data
            last_datetime = datetime.fromtimestamp(current_data[-1]['t'] / 1000) + timedelta(hours=1)
        data = pd.DataFrame(data)
        data.rename({
            'o': 'open',
            'h': 'high',
            'l': 'low',
            'c': 'close',
            'v': 'volume',
            't': 'date'
        }, inplace=True, axis=1)
        data.index = pd.to_datetime(data['date'], unit='ms')
        data.drop(columns=['date', 'vw', 'n'], inplace=True)
        data = self.normalizeColumnsOrder(data)
        return data

    def getAvailablePairs(self, market : str = 'crypto') -> List[str]:
        """Return the list of available pairs

        Returns:
            List[str]: the list of available pairs
        """
        url = f'https://api.polygon.io/v3/reference/tickers?market={market}&active=true&sort=ticker&order=asc&limit=5000&apiKey=8RvtCtdRW2bFH8WBE9JoihuwmnFECybm'
        json = r.get(url).json()
        pairs = []
        
        for pair in json['results']:
            ticker = pair['ticker']
            if ticker.startswith('X:'):
                ticker = ticker[2:]
            pairs.append(ticker)
        pairs.sort()
        return pairs
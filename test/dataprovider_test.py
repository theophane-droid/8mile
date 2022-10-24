from datetime import datetime
import pytz
import os

from Hmile.DataProvider import (YahooDataProvider,
                                CSVDataProvider,
                                ElasticDataProvider,
                                PolygonDataProvider)
from Hmile.Exception import (DataProviderArgumentException, 
                             DataframeFormatException,
                             DataNotAvailableException)
from Hmile.FillPolicy import FillPolicyAkima

import pandas as pd

import unittest

class TestCheckArguments(unittest.TestCase):
    def test_start_after_end(self):
        with self.assertRaises(DataProviderArgumentException):
            self.dp = YahooDataProvider(['BTCUSD'], '2022-01-02', '2022-01-01', interval='hour')
            
    def test_not_pair(self):
        with self.assertRaises(DataProviderArgumentException):
            self.dp = YahooDataProvider(None, '2022-01-01', '2022-01-02', interval='hour')
            
    def test_not_start(self):
        with self.assertRaises(DataProviderArgumentException):
             self.dp = YahooDataProvider(['BTCUSD'], None, '2022-01-02', interval='hour')
    
    def test_not_end(self):
        with self.assertRaises(DataProviderArgumentException):
             self.dp = YahooDataProvider(['BTCUSD'], '2022-01-01', None, interval='hour')

    def test_not_interval(self):
        with self.assertRaises(DataProviderArgumentException):
             self.dp = YahooDataProvider(['BTCUSD'], '2022-01-01', '2022-01-02', interval=None)
    
    def test_format_date_error(self):
        with self.assertRaises(DataProviderArgumentException):
             self.dp = YahooDataProvider(['BTCUSD'], 'sh3lby', '2022-01-02', interval=None)

class TestCheckDataframe(unittest.TestCase):
    def setUp(self):
        self.dp = YahooDataProvider(['BTCUSD'], '2022-01-01', '2022-01-03', interval='hour')
        
    def test_working(self):
        dataframe = pd.DataFrame({'date': ['2021-01-01', '2021-01-02', '2021-01-03'], 'open': [1, 2, 3], 'high': [3, 4, 5], 'low': [5, 6, 7], 'close': [7, 8, 9], 'volume': [9, 10, 11]})
        dataframe.index = pd.to_datetime(dataframe['date'])
        dataframe.drop(columns=['date'], inplace=True)
        self.dp.checkDataframe(dataframe)
    
    def test_columns_order(self):
        dataframe = pd.DataFrame({'date': ['2021-01-01', '2021-01-02'], 'high': [3, 4], 'open': [1, 2], 'low': [5, 6], 'close': [7, 8], 'volume': [9, 10]})
        with self.assertRaises(DataframeFormatException):
            self.dp.checkDataframe(dataframe)
    
    def test_index_not_date(self):
        dataframe = pd.DataFrame({'date': ['sh3lby', '33'], 'high': [3, 4], 'open': [1, 2], 'low': [5, 6], 'close': [7, 8], 'volume': [9, 10]})
        with self.assertRaises(DataframeFormatException):
            self.dp.checkDataframe(dataframe)
    
    def test_no_monotonic_increasing(self):
        dataframe = pd.DataFrame({'date': ['2021-01-01', '2021-01-02', '2021-01-05'], 'high': [3, 4, 5], 'open': [1, 2, 3], 'low': [5, 6, 7], 'close': [7, 8, 9], 'volume': [9, 10, 11]})
        with self.assertRaises(DataframeFormatException):
            self.dp.checkDataframe(dataframe)
    
    def test_not_uniq_index(self):
        dataframe = pd.DataFrame({'date': ['2021-01-01', '2021-01-01'], 'high': [3, 4], 'open': [1, 2], 'low': [5, 6], 'close': [7, 8], 'volume': [9, 10]})
        with self.assertRaises(DataframeFormatException):
            self.dp.checkDataframe(dataframe)
            
class TestNormalizeColumnsOrder(unittest.TestCase):
    def setUp(self):
        self.dp = YahooDataProvider(['BTCUSD'], '2022-01-01', '2022-01-03', interval='hour')
        self.dataframe = pd.DataFrame({'close': [7, 8], 'sh3lby2' : [1,2], 'sh3lby1' : [1,2], 'volume': [9, 10], 'high': [3, 4], 'open': [1, 2], 'low': [5, 6]})

    def test_normalize_columns_order(self):
        result = self.dp.normalizeColumnsOrder(self.dataframe)
        self.assertEqual(result.columns.tolist(), ['open', 'high', 'low', 'close', 'volume', 'sh3lby1', 'sh3lby2'])


class TestYahooFinanceDataProvider(unittest.TestCase):
    def test_normal(self):
        self.dp = YahooDataProvider(['BTCUSD'], '2022-01-01', '2022-01-03', interval='hour')
        self.dp.fill_policy = FillPolicyAkima('hour')
        data = self.dp.getData()
        self.dp.checkDataframe(data['BTCUSD'])

class TestCSVDataProvider(unittest.TestCase):
    def test_normal(self):
        self.dp = CSVDataProvider(['BTCUSD'], '2022-01-01', '2022-01-03', 'test/data/csvdataprovider', interval='hour')
        data = self.dp.getData()
        self.dp.checkDataframe(data['BTCUSD'])

class TestElasticDataProvider(unittest.TestCase):
    def setUp(self) -> None:
        self.elastic_url = os.environ['ELASTIC_URL']
        self.elastic_user = os.environ['ELASTIC_USER']
        self.elastic_pass = os.environ['ELASTIC_PASS']
        
    def test_normal(self):
        self.dp = ElasticDataProvider(
            ['BTCUSD'],
            '2022-01-01',
            '2022-01-03',
            self.elastic_url,
            self.elastic_user,
            self.elastic_pass,
            interval='hour'
        )
        data = self.dp.getData()
        self.dp.checkDataframe(data['BTCUSD'])
    
class TestPolygonDataProvider(unittest.TestCase):
    def setUp(self) -> None:
        self.polygon_key = os.environ['POLYGON_API_KEY']
    def test_normal(self):
        self.dp = PolygonDataProvider(
            ['BTCUSD'],
            '2022-01-01',
            '2022-01-03',
            self.polygon_key,
            'day')
        data = self.dp.getData()
        self.dp.checkDataframe(data['BTCUSD'])
        
class TestMultiPairYahoo(unittest.TestCase):
    def setUp(self) -> None:
        self.dp = YahooDataProvider(
            ['BTCUSD', 'ETHUSD'],
            '2022-01-01',
            '2022-01-03',
            'hour'
        )
    def test_normal(self):
        data = self.dp.getData()
        self.dp.checkDataframe(data['BTCUSD'])
        self.dp.checkDataframe(data['ETHUSD'])

class TestPairNotAvailable(unittest.TestCase):
    def setUp(self) -> None:
        es_url = os.environ['ELASTIC_URL']
        es_user = os.environ['ELASTIC_USER']
        es_pass = os.environ['ELASTIC_PASS']
        self.dp_es = ElasticDataProvider(
            ['BLABLA'],
            '2022-01-01',
            '2022-01-03',
            es_url,
            es_user,
            es_pass,
            interval='hour'
        )
        self.dp_csv = CSVDataProvider(
            ['BLABLA'],
            '2022-01-01',
            '2022-01-03',
            'test/data/csvdataprovider',
            interval='hour'
        )
        self.dp_yahoo = YahooDataProvider(
            ['BLABLA'],
            '2022-01-01',
            '2022-01-03',
            interval='hour'
        )
        polygon_key = os.environ['POLYGON_API_KEY']
        self.dp_polygon = PolygonDataProvider(
            ['BLABLA'],
            '2022-01-01',
            '2022-01-03',
            polygon_key,
            interval='hour'
        )
    def test_elastic(self):
        with self.assertRaises(DataNotAvailableException):
            self.dp_es.getData()

    def test_csv(self):
        with self.assertRaises(DataNotAvailableException):
            self.dp_csv.getData()
    
    def test_yahoo(self):
        with self.assertRaises(DataNotAvailableException):
            self.dp_yahoo.getData()
            
    def test_polygon(self):
        with self.assertRaises(DataNotAvailableException):
            self.dp_polygon.getData()


class TestDateNotAvailable(unittest.TestCase):
    def setUp(self) -> None:
        es_url = os.environ['ELASTIC_URL']
        es_user = os.environ['ELASTIC_USER']
        es_pass = os.environ['ELASTIC_PASS']
        self.dp_es = ElasticDataProvider(
            ['BTCUSD'],
            '2050-01-01',
            '2050-01-03',
            es_url,
            es_user,
            es_pass,
            interval='hour'
        )
        self.dp_csv = CSVDataProvider(
            ['BTCUSD'],
            '2050-01-01',
            '2050-01-03',
            'test/data/csvdataprovider',
            interval='hour'
        )
        self.dp_yahoo = YahooDataProvider(
            ['BTCUSD'],
            '2050-01-01',
            '2050-01-03',
            interval='hour'
        )
        polygon_key = os.environ['POLYGON_API_KEY']
        self.dp_polygon = PolygonDataProvider(
            ['BTCUSD'],
            '2050-01-01',
            '2050-01-03',
            polygon_key,
            interval='hour'
        )
    def test_elastic(self):
        with self.assertRaises(DataNotAvailableException):
            self.dp_es.getData()

    def test_csv(self):
        with self.assertRaises(DataNotAvailableException):
            self.dp_csv.getData()
    
    def test_yahoo(self):
        with self.assertRaises(DataNotAvailableException):
            self.dp_yahoo.getData()
            
    def test_polygon(self):
        with self.assertRaises(DataNotAvailableException):
            self.dp_polygon.getData()
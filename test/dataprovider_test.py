from datetime import datetime
import pytz

from Hmile.DataProvider import DataProvider, YahooDataProvider, CSVDataProvider
from Hmile.Exception import DataProviderArgumentException, DataframeFormatException

import pandas as pd

import unittest

class TestCheckArguments(unittest.TestCase):
    def test_start_after_end(self):
        with self.assertRaises(DataProviderArgumentException):
            self.dp = YahooDataProvider('BTCUSD', '2022-01-02', '2022-01-01', interval='hour')
            
    def test_not_pair(self):
        with self.assertRaises(DataProviderArgumentException):
            self.dp = YahooDataProvider(None, '2022-01-01', '2022-01-02', interval='hour')
            
    def test_not_start(self):
        with self.assertRaises(DataProviderArgumentException):
             self.dp = YahooDataProvider('BTCUSD', None, '2022-01-02', interval='hour')
    
    def test_not_end(self):
        with self.assertRaises(DataProviderArgumentException):
             self.dp = YahooDataProvider('BTCUSD', '2022-01-01', None, interval='hour')

    def test_not_interval(self):
        with self.assertRaises(DataProviderArgumentException):
             self.dp = YahooDataProvider('BTCUSD', '2022-01-01', '2022-01-02', interval=None)
    
    def test_format_date_error(self):
        with self.assertRaises(DataProviderArgumentException):
             self.dp = YahooDataProvider('BTCUSD', 'sh3lby', '2022-01-02', interval=None)

class TestCheckDataframe(unittest.TestCase):
    def setUp(self):
        self.dp = YahooDataProvider('BTCUSD', '2022-01-01', '2022-01-03', interval='hour')
        
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
        self.dp = YahooDataProvider('BTCUSD', '2022-01-01', '2022-01-03', interval='hour')
        self.dataframe = pd.DataFrame({'close': [7, 8], 'sh3lby2' : [1,2], 'sh3lby1' : [1,2], 'volume': [9, 10], 'high': [3, 4], 'open': [1, 2], 'low': [5, 6]})

    def test_normalize_columns_order(self):
        result = self.dp.normalizeColumnsOrder(self.dataframe)
        self.assertEqual(result.columns.tolist(), ['open', 'high', 'low', 'close', 'volume', 'sh3lby1', 'sh3lby2'])

class TestWorking(unittest.TestCase):
    def test_normal(self):
        # assert works
        self.dp = YahooDataProvider('BTCUSD', '2022-01-01', '2022-01-03', interval='day')
        data = self.dp.getData()
        self.assertEqual(data.columns.tolist(), ['open', 'high', 'low', 'close', 'volume'])
        index = [d.to_pydatetime() for d in data.index]
        asserted = [ d.to_pydatetime() for d in pd.date_range(start='2022-01-01', end='2022-01-03', freq='D')] 
        self.assertEqual(index, asserted)


class TestYahooFinanceDataProvider(unittest.TestCase):
    def test_normal(self):
        self.dp = YahooDataProvider('BTCUSD', '2022-01-01', '2022-01-03', interval='hour')
        self.dp.getData()


class TestCSVDataProvider(unittest.TestCase):
    def test_normal(self):
        self.dp = CSVDataProvider('BTCUSD', '2022-01-01', '2022-01-03', 'test/data/csvdataprovider', interval='hour')
        self.dp.getData()
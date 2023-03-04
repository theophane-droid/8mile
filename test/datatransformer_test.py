import os
import sys
import unittest
from hmile.DataProvider import CSVDataProvider, ElasticDataProvider
from hmile.FillPolicy import FillPolicyAkima
from hmile.DataTransformer import TaDataTransformer
from hmile.DataExporter import CSVDataExporter

class TestTaFeaturesTransformer(unittest.TestCase):
    
    def setUp(self):
        self.start_date = '2021-12-05'
        self.end_date = '2021-12-17'
        self.dp = CSVDataProvider(
            ['BTCUSD'],
            self.start_date,
            self.end_date,
            directory='test/data/csvdataprovider',
            interval='hour'
        )
        self.dp.fill_policy = FillPolicyAkima('hour')
        self.transformer = TaDataTransformer(self.dp)

    def test_transform(self) :
        df = self.transformer.transform()['BTCUSD']
        self.assertIsNotNone(df)
        self.assertGreater(len(df.columns), 50)
        self.assertEqual(df.index[0].strftime('%Y-%m-%d'), self.start_date)
        self.assertEqual(df.index[-1].strftime('%Y-%m-%d'), self.end_date)


class FalseDataProvider:
    start_date = '2021-12-05'
    end_date = '2021-12-17'
    interval = 'hour'


class TestTransformer(unittest.TestCase):
    def setUp(self):
        self.transformer = TaDataTransformer(FalseDataProvider())

    def test_transform(self) :
        with self.assertRaises(TypeError):
            self.transformer.transform()

class TestExportFromDatatransformer(unittest.TestCase):
    # ref issue #14
    def setUp(self):
        
        self.dp = CSVDataProvider(
            ['BTCUSD'],
            '2021-12-05',
            '2021-12-17',
            directory='test/data/csvdataprovider',
            interval='hour'
        )
        self.dp.fill_policy = FillPolicyAkima('hour')
        self.transformer = TaDataTransformer(self.dp)
        self.exporter = CSVDataExporter(self.transformer, 'test/data/csvdataexporter')
    
    def test_export(self) :
        self.exporter.export()
        self.assertTrue(os.path.exists('test/data/csvdataexporter/f-btcusd-hour.csv'))
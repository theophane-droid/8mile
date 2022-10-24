import os
import sys
import unittest
from Hmile.DataProvider import CSVDataProvider, ElasticDataProvider
from Hmile.FillPolicy import FillPolicyAkima
from Hmile.utils import trainAE, concatAndNormDf
from Hmile.DataTransformer import TaDataTransformer
from Hmile.DataExporter import CSVDataExporter

class TestTrainAE(unittest.TestCase):
    
    def setUp(self):
        self.elastic_url = os.environ['ELASTIC_URL']
        self.elastic_user = os.environ['ELASTIC_USER']
        self.elastic_pass = os.environ['ELASTIC_PASS']
        self.dp = ElasticDataProvider(
            ['BTCUSD', 'ETHUSD'],
            '2020-01-01',
            '2022-01-03',
            es_url=self.elastic_url,
            es_user=self.elastic_user,
            es_pass=self.elastic_pass,
            interval='hour'
        )
        self.dp.fill_policy = FillPolicyAkima('hour')
        self.transformer = TaDataTransformer(self.dp)


    def test_normalization_concat(self) :
        pairs = ['BTCUSD', 'ETHUSD']
        df2,norm = concatAndNormDf(self.transformer.transform(), True)
        self.assertEqual(self.transformer.transform()["BTCUSD"].shape[0]+self.transformer.transform()["ETHUSD"].shape[0],df2.shape[0])
        for i in pairs :
            self.assertTrue(norm.__contains__(i))
            self.assertEqual(norm[i]["mean"].index.values.tolist(),df2.columns.values.tolist())
            self.assertEqual(norm[i]["std"].index.values.tolist(),df2.columns.values.tolist())
        self.assertTrue(not df2.isnull().values.any())

    def test_trainae(self) :
        df = self.transformer.transform()
        AE = trainAE(df,nb_epoch=10)
        self.assertIsNotNone(AE)

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
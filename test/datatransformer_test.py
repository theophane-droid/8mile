import os
import unittest
from Hmile.DataProvider import CSVDataProvider, ElasticDataProvider
from Hmile.FillPolicy import FillPolicyAkima
from Hmile.DataTransformer import TaFeaturesTransformer
from Hmile.utils import trainAE

class TestTransformer(unittest.TestCase):
    
    def setUp(self):
        self.elastic_url = os.environ['ELASTIC_URL']
        self.elastic_user = os.environ['ELASTIC_USER']
        self.elastic_pass = os.environ['ELASTIC_PASS']
        self.dp = ElasticDataProvider('BTCUSD', '2020-01-01', '2022-01-03', es_url=self.elastic_url, es_user=self.elastic_user, es_pass=self.elastic_pass, interval='hour')
        self.dp.fill_policy = FillPolicyAkima('hour')
        self.transformer = TaFeaturesTransformer(self.dp)

    def test_trainAE(self) :
        df = self.transformer.transform()
        AE = trainAE(df,nb_epoch=10)
        self.assertIsNotNone(AE)

import unittest

from Hmile.DataProvider import CSVDataProvider
from Hmile.FillPolicy import FillPolicyAkima
from Hmile.DataTransformer import TaFeaturesTransformer

class TestTransformer(unittest.TestCase):
    
    def setUp(self):
        self.dp = CSVDataProvider('BTCUSD', '2021-01-01', '2022-01-03', 'test/data/csvdataprovider', interval='hour')
        self.dp.fill_policy = FillPolicyAkima('hour')
        self.transformer = TaFeaturesTransformer(self.dp)
        
    def test(self):
        nb_col = self.transformer.transform().shape[1]
        self.assertEqual(nb_col, 283)
import unittest
from Hmile.DataProvider import CSVDataProvider, ElasticDataProvider
from Hmile.FillPolicy import FillPolicyAkima
from Hmile.DataTransformer import TaFeaturesTransformer
from Hmile.utils import trainAE

ELASTIC_USER=''
ELASTIC_PASS=''
ELASTIC_URL = ''
class TestTransformer(unittest.TestCase):
    
    def setUp(self):
        self.dp = ElasticDataProvider('BTCUSD', '2020-01-01', '2022-01-03', es_url=ELASTIC_URL, es_user=ELASTIC_USER, es_pass=ELASTIC_PASS, interval='hour')
        self.dp.fill_policy = FillPolicyAkima('hour')
        self.transformer = TaFeaturesTransformer(self.dp)
        
    def test(self):
        nb_col = self.transformer.transform().shape[1]
        print(type(self.transformer.transform()))
        self.assertEqual(nb_col, 493)
    def test_trainAE(self) :
        df = self.transformer.transform()
        AE = trainAE(df,nb_epoch=10)
        self.assertIsNotNone(AE)

        


if __name__ == '__main__':
    unittest.main()
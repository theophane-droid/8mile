import os
import unittest

from hmile.DataProvider import CSVDataProvider
from hmile.FillPolicy import FillPolicyAkima
from hmile.DataExporter import CSVDataExporter, ElasticDataExporter

class TestCSVDataExporter(unittest.TestCase):
    
    def setUp(self):
        directory = '/tmp/testtransformer'
        # create directory if not exists
        try:
            os.mkdir(directory)
        except FileExistsError:
            pass
        self.dp = CSVDataProvider(['BTCUSD'], '2021-01-01', '2022-01-03', 'test/data/csvdataprovider', interval='hour')
        self.dp.fill_policy = FillPolicyAkima('hour')
        self.exporter = CSVDataExporter(self.dp, directory)
        
    def test(self):
        self.exporter.export()
        self.assertTrue(os.path.isfile('/tmp/testtransformer/f-btcusd-hour.csv'))
        

# TODO : setup test instance
# class TestElasticDataExporter(unittest.TestCase):
#     def setUp(self) -> None:
#         self.elastic_url = os.environ['ELASTIC_URL']
#         self.elastic_user = os.environ['ELASTIC_USER']
#         self.elastic_pass = os.environ['ELASTIC_PASS']
#         self.dp = CSVDataProvider(['BTCUSD'], '2021-01-01', '2022-01-03', 'test/data/csvdataprovider', interval='hour')
#         self.dp.fill_policy = FillPolicyAkima('hour')
#         self.exporter = ElasticDataExporter(
#             self.dp,
#             self.elastic_url,
#             self.elastic_user,
#             self.elastic_pass
#         )
        
#     def test_normal(self):
#         self.exporter.export()
        
class MultiCSVExport(unittest.TestCase):
    def setUp(self):
        directory = '/tmp/testtransformer'
        # create directory if not exists
        try:
            os.mkdir(directory)
        except FileExistsError:
            pass
        self.dp = CSVDataProvider(['BTCUSD', 'ETHUSD'], '2021-01-01', '2022-01-03', 'test/data/csvdataprovider', interval='hour')
        self.dp.fill_policy = FillPolicyAkima('hour')
        self.exporter = CSVDataExporter(self.dp, directory)
        
    def test(self):
        self.exporter.export()
        self.assertTrue(os.path.isfile('/tmp/testtransformer/f-btcusd-hour.csv'))
        self.assertTrue(os.path.isfile('/tmp/testtransformer/f-ethusd-hour.csv'))
    
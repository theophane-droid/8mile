import os
import unittest

from Hmile.DataProvider import CSVDataProvider
from Hmile.FillPolicy import FillPolicyAkima
from Hmile.DataExporter import CSVDataExporter

class TestTransformer(unittest.TestCase):
    
    def setUp(self):
        directory = '/tmp/testtransformer'
        # create directory if not exists
        try:
            os.mkdir(directory)
        except FileExistsError:
            pass
        self.dp = CSVDataProvider('BTCUSD', '2021-01-01', '2022-01-03', 'test/data/csvdataprovider', interval='hour')
        self.dp.fill_policy = FillPolicyAkima('hour')
        self.exporter = CSVDataExporter(self.dp, directory)
        
    def test(self):
        self.exporter.export()
        self.assertTrue(os.path.isfile('/tmp/testtransformer/f-btcusd-hour.csv'))
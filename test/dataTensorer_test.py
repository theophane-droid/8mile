import unittest
import yaml

class TestSingleFeatururesDatatensorer(unittest.TestCase):
    def setUp(self) -> None:
        test_cfg = yaml.dump(yaml.load("tensorTest.yaml"))
    def test_creation(self):
        data = self.dp.getData()
        self.dp.checkDataframe(data['BTCUSD'])
        self.dp.checkDataframe(data['ETHUSD'])

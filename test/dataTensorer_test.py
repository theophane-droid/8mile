import unittest
import yaml
import os
import torch
from Hmile.DataTensorer import SingleFeaturesDataTensorer

class TestSingleFeatururesDatatensorer(unittest.TestCase):
    def setUp(self) -> None:
        test_cfg = {}
        with open("test/tensorTest.yaml", 'r') as stream:
            test_cfg = yaml.safe_load(stream)
        test_cfg = test_cfg["tensorer"]
        es_id = {
            "es_url" : os.environ['ELASTIC_URL'],
            "es_user" : os.environ['ELASTIC_USER'],
            "es_pass" : os.environ['ELASTIC_PASS']
        }

        test_cfg["provider_configuration"] = es_id
        search = test_cfg["encoder_configuration"]["searching_args"]
        test_cfg["encoder_configuration"] = es_id.copy()
        test_cfg["encoder_configuration"]["searching_args"] = search
        self.cfg = test_cfg

    def test_creation(self):
        self.dt1 = SingleFeaturesDataTensorer(**self.cfg)
        del self.cfg["encoder_configuration"]
        dt2 = SingleFeaturesDataTensorer(**self.cfg)
        self.assertIsNotNone(self.dt1)
        self.assertIsNotNone(dt2)
        



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
        
    def test_get_indicators(self):
        for _ in range(10) :
            ind = self.dt1.current_step[:]
            self.dt1.get_indicators()
            self.assertTrue(self.dt1.current_step[:,1] == ind[:,1]+1)
            self.assertTrue(self.dt1.current_step[:,0] == ind[:,0])

    def test_reset(self) :
        self.dt1.reset()
        for _ in range(20) :
            self.dt1.get_indicators()
        ind_to_reset = torch.zeros(self.dt1.nb_env)
        ind_to_reset[[0,3,4,10,15]] = 1
        prev_step = self.dt1.current_step[:]
        self.dt1.reset_by_id(ind_to_reset)
        self.assertTrue(prev_step[ind_to_reset] != self.dt1.current_step[ind_to_reset])
        ind_to_reset = torch.ones(self.dt1.nb_env)-ind_to_reset
        self.assertTrue(prev_step[ind_to_reset] == self.dt1.current_step[ind_to_reset])

        self.assertTrue


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
        dt1 = SingleFeaturesDataTensorer(**self.cfg)
        del self.cfg["encoder_configuration"]
        dt2 = SingleFeaturesDataTensorer(**self.cfg)
        self.assertIsNotNone(dt1)
        self.assertIsNotNone(dt2)

    def test_get_indicators(self):
        dt1 = SingleFeaturesDataTensorer(**self.cfg)

        for _ in range(10) :
            ind = dt1.current_step.detach().clone()
            dt1.get_indicators()
            self.assertTrue(torch.all(dt1.current_step[:,1] == (ind[:,1]+1)))
            self.assertTrue(torch.all(dt1.current_step[:,0] == ind[:,0]))

    def test_reset(self) :
        dt1 = SingleFeaturesDataTensorer(**self.cfg)

        dt1.reset()
        for _ in range(20) :
            dt1.get_indicators()
        ind_to_reset = torch.tensor([0,3,4,10,15],dtype=torch.long)
        ind_to_verif = torch.tensor([1,2,5,6,7,8,9,11,12,13,14],dtype=torch.long)

        prev_step = dt1.current_step.detach().clone()
        dt1.reset_by_id(ind_to_reset)
        self.assertTrue(torch.any(prev_step[ind_to_reset,0] != dt1.current_step[ind_to_reset,0]))
        self.assertTrue(torch.any(prev_step[ind_to_reset,1] != dt1.current_step[ind_to_reset,1]))

        self.assertTrue(torch.all(prev_step[ind_to_verif,0] == dt1.current_step[ind_to_verif,0]))
        self.assertTrue(torch.all(prev_step[ind_to_verif,1] == dt1.current_step[ind_to_verif,1]))





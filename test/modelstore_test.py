import time
import os
from datetime import datetime
import torch.nn as nn
import unittest

from Hmile.ModelStore import MetaModel, ElasticModelStore

class ModelStoreTest(unittest.TestCase):
    # ref #25
    def setUp(self):
        self.model = nn.Sequential(
            nn.Linear(10, 20)
        )

    def test(self):
        meta_model = MetaModel(
            self.model,
            0.8,
            'test',
            ['a', 'b', 'c'],
            ['tag1', 'tag2']
        )
        now = datetime.now()
        dict = meta_model.__dict__()
        self.assertTrue('model' in dict)
        self.assertEqual(dict['performance'], 0.8)
        self.assertEqual(dict['description'], 'test')
        self.assertEqual(dict['columns_list'], ['a', 'b', 'c'])
        self.assertEqual(dict['tags'], ['tag1', 'tag2'])
        self.assertEqual(dict['creation_date'].year, now.year)
        self.assertEqual(dict['creation_date'].month, now.month)
        self.assertEqual(dict['creation_date'].day, now.day)

class ElasticModelStoreTest(unittest.TestCase):
    # ref #25
    def setUp(self):
        self.model = nn.Sequential(
            nn.Linear(10, 20)
        )
        self.meta_model = MetaModel(
            self.model,
            0.8,
            'test',
            ['a', 'b', 'c'],
            ['test_tag']
        )
        url = os.environ['ELASTIC_URL']
        user = os.environ['ELASTIC_USER']
        pass_ = os.environ['ELASTIC_PASS']
        self.storer = ElasticModelStore(url, user, pass_)    
        self.storer.store(self.meta_model)

    def test_metamodelstored(self):
        result = self.storer.get(performance=0.8)
        self.assertGreater(len(result), 0)
        dict1 = self.meta_model.__dict__()
        del dict1['model']
        dict2 = result[-1].__dict__()
        del dict2['model']
        self.assertEqual(dict1, dict2)
    
    def test_modeltype(self):
        result = self.storer.get(tags='test_tag')[-1]
        self.assertTrue(type(result.model) == nn.Sequential)

class ElasticRecursiveSearch(unittest.TestCase):
    def setUp(self):
        self.storer = ElasticModelStore(
            os.environ['ELASTIC_URL'],
            os.environ['ELASTIC_USER'],
            os.environ['ELASTIC_PASS']
        )
        self.model = nn.Sequential(
            nn.Linear(10, 20)
        )
        for _ in range(10):
            self.meta_model = MetaModel(
                
                self.model,
                0.8,
                'test',
                ['a', 'b', 'c'],
                ['recursive_test_tag']
            )
            self.meta_model.meta['meta_field'] = 'meta_value'
            self.storer.store(self.meta_model)
    
    def test(self):
        result = self.storer.get(tags='recursive_test_tag', limit=3)
        self.assertGreater(len(result), 0)
        self.assertEqual(len(result) % 10, 0)

class MetaFieldTest(unittest.TestCase):
    # ref issus #22
    def setUp(self):
        self.model = nn.Sequential(
            nn.Linear(10, 20)
        )
        self.meta_model = MetaModel(
            self.model,
            0.8,
            'meta_test',
            ['a', 'b', 'c'],
            ['meta_test', 'tag2'],
            meta={'meta_field': 'meta_value'}
        )
        url = os.environ['ELASTIC_URL']
        user = os.environ['ELASTIC_USER']
        pass_ = os.environ['ELASTIC_PASS']
        self.storer = ElasticModelStore(url, user, pass_)
        self.storer.store(self.meta_model)
    
    def test(self):
        # get meta_test
        results = self.storer.get(tags='meta_test')[-1]
        self.assertEqual(results.meta['meta_field'], 'meta_value')

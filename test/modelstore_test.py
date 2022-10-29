import time
import os
from datetime import datetime
import torch.nn as nn
import unittest

from elasticsearch import Elasticsearch
from Hmile.ModelStore import MetaModel, ElasticModelStore

url = os.environ['ELASTIC_URL']
user = os.environ['ELASTIC_USER']
pass_ = os.environ['ELASTIC_PASS']

def remove_index(index_name):
    es = Elasticsearch(
            [os.environ['ELASTIC_URL']],
            http_auth=(os.environ['ELASTIC_USER'], os.environ['ELASTIC_PASS']),
            http_compress=True, verify_certs=False
    )
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)

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

    @staticmethod
    def tearDown():
        remove_index('test_models')

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
        self.index_name = 'test_models_' + str(time.time())
        self.storer = ElasticModelStore(url, user, pass_, index_name=self.index_name)    
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
        result = self.storer.get(tags=['test_tag'])[-1]
        self.assertTrue(type(result.model) == nn.Sequential)

    def tearDown(self):
        remove_index(self.index_name)


class ElasticRecursiveSearch(unittest.TestCase):
    def setUp(self):
        self.index_name = 'test_models_' + str(time.time())
        self.storer = ElasticModelStore(url, user, pass_, index_name=self.index_name)    
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
        result = self.storer.get(tags=['recursive_test_tag'], limit=3)
        self.assertGreater(len(result), 0)
        self.assertEqual(len(result) % 10, 0)

    def tearDown(self):
        remove_index(self.index_name)

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
        self.index_name = 'test_models_' + str(time.time())
        self.storer = ElasticModelStore(url, user, pass_, index_name=self.index_name)    
        self.storer.store(self.meta_model)
    
    def test(self):
        # get meta_test
        results = self.storer.get(tags=['meta_test'])[-1]
        self.assertEqual(results.meta['meta_field'], 'meta_value')

    def tearDown(self):
        remove_index(self.index_name)

class TestMultiTags(unittest.TestCase):
    # ref #33
    def setUp(self):
        self.model = nn.Sequential(
            nn.Linear(10, 20)
        )
        self.tag_time = str(time.time())
        self.meta_model1 = MetaModel(
            self.model,
            0.8,
            'meta_test',
            ['a', 'b', 'c'],
            [self.tag_time, 'tag1'],
            meta={'meta_field': 'meta_value'}
        )
        self.meta_model2 = MetaModel(
            self.model,
            0.8,
            'meta_test',
            ['a', 'b', 'c'],
            [self.tag_time, 'tag2'],
            meta={'meta_field': 'meta_value'}
        )
        self.index_name = 'test_models_' + str(time.time())
        self.storer = ElasticModelStore(url, user, pass_, index_name=self.index_name)    
        self.storer.store(self.meta_model1)
        self.storer.store(self.meta_model2)
        
    def test(self):
        results = self.storer.get(tags=[self.tag_time, 'tag1'])
        self.assertEqual(len(results), 1)
        results = self.storer.get(tags=[self.tag_time, 'tag2'])
        self.assertEqual(len(results), 1)

    def tearDown(self):
        remove_index(self.index_name)
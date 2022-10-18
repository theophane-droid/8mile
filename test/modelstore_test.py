import shutil
import os
from datetime import datetime
import torch.nn as nn
import unittest

from Hmile.ModelStore import MetaModel, ModelStore, ElasticMetaModelStore, LocalModelStore

class ModelStoreTest(unittest.TestCase):
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
        self.assertEqual(dict['performance'], 0.8)
        self.assertEqual(dict['description'], 'test')
        self.assertEqual(dict['columns_list'], ['a', 'b', 'c'])
        self.assertEqual(dict['tags'], ['tag1', 'tag2'])
        self.assertEqual(dict['creation_date'].year, now.year)
        self.assertEqual(dict['creation_date'].month, now.month)
        self.assertEqual(dict['creation_date'].day, now.day)
        
class ElasticMetaModelStoreTest(unittest.TestCase):
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
        self.storer = ElasticMetaModelStore(url, user, pass_)
        self.storer.store(self.meta_model)

    def test_metamodelstored(self):
        result = self.storer.get('test_tag')
        self.assertGreater(len(result), 0)
        dict = self.meta_model.__dict__()
        self.assertEqual(result['performance'], dict['performance'])
        self.assertEqual(result['description'], dict['description'])
        self.assertEqual(result['columns_list'], dict['columns_list'])
        self.assertEqual(result['tags'], dict['tags'])
        self.assertEqual(result['performance'], dict['performance'])

class LocalModelStoreTest(unittest.TestCase):
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
        self.storer = LocalModelStore('models')
        if os.path.exists('models'):
            shutil.rmtree('models')
    
    def test_store(self):
        self.storer.store(self.meta_model)
        result = self.storer.get(self.meta_model)
        self.assertTrue(os.path.exists('models'))
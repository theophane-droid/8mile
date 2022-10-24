import os
import time
from datetime import datetime
from unittest import result
import torch
from torch import nn
from abc import abstractmethod
from elasticsearch import Elasticsearch

class MetaModel:
    """
    This objet is used to store the model and to get it back from a model store. It also stores meta informations about the model.
    
    :ivar model: the pytorch model. Can be None if no model is associated with the MetaModel
    :ivar performance: an arbitrary number between 0 and 1 to describe the performance of the model 
    :ivar description: a concise description of the model
    :ivar columns_list: an ordered list of the columns used to train the model
    :ivar tags: keywords to describe the model. This is the key value to search a MetaModel from a MetaModelStore
    :ivar creation_date: the datetime object when the model was created
    """
    def __init__(self,
            model: nn.Module,
            performance: float,
            description: str,
            columns_list: list,
            tags : list,
            creation_date  : datetime = None,
            meta : dict = {}):
            """Create a MetaModel object.
                model (nn.Module): The model to store.
                performance (float): A arbitrary number to describe the performance of the model between 0 and 1.
                description (str): A concise description of the model.
                columns_list (list): An ordered list of the columns used to train the model.
                tags (list) : Keywords to describe the model. Can be use to filter the model store.
                creation_date (_type_, optional): _description_. Defaults to now
                meta (dict, optional): A dictionary to store any other information about the model. Defaults to {}.
            """
            self.model = model
            self.performance = performance
            self.description = description
            self.columns_list = columns_list
            self.tags = tags
            self.meta = meta
            if type(creation_date) != type(None):
                self.creation_date = creation_date
            else:
                self.creation_date = datetime.now()
    
    def __dict__(self):
        return {
                'performance' : self.performance,
                'description' : self.description,
                'columns_list' : self.columns_list,
                'tags' : self.tags,
                'creation_date' : self.creation_date,
                'meta' : self.meta
        }

class MetaModelStore:
    def __init__(self):
        """Abstraction to store meta values about models
        """
        pass
    
    @abstractmethod
    def store(self, meta_model : MetaModel):
        """Store a MetaModel object

        Args:
            meta_model (MetaModel): MetaModel object to store
        """
        raise NotImplementedError()
    
    @abstractmethod
    def get(self, tag : str):
        """Get back a list of meta objects, corresponding to the tag. Each meta model which contains this tag once will be returned.

        Args:
            tag (str): tag to filter the meta objects

        """
        raise NotImplementedError()
    
class ModelStore:
    def __init__(self):
        """Abstraction to store model
        """
        raise NotImplementedError()
    
    @abstractmethod
    def store(self, meta_model : MetaModel):
        """Store the torch model contained in meta_model.model.

        Args:
            meta_model (MetaModel): MetaModel object to store
        """
        raise NotImplementedError()
    
    @abstractmethod
    def get(self, meta_model : MetaModel):
        """Get back a meta objects filled with the model. The model will be referenced as meta_model.model.

        Args:
            meta_model (str): meta_model to get the model back

        """
        raise NotImplementedError()

class ElasticMetaModelStore(MetaModelStore):
    """Store meta models information in ElasticSearch in the index 'models'
    """
    def __init__(self, es_url : str, es_user : str, es_pass : str):
        self.es_url = es_url
        self.es_user = es_user
        self.es_pass = es_pass
    
    def store(self, meta_model : MetaModel):
        index_name = 'models'
        es = Elasticsearch(self.es_url, http_compress=True, verify_certs=False, http_auth=(self.es_user, self.es_pass))
        es.index(index=index_name, document=meta_model.__dict__())
        # we wait for the document to be indexed
        time.sleep(5)
    
    def get(self, tag : str) -> list:
        index_name = 'models'
        es = Elasticsearch(self.es_url, http_compress=True, verify_certs=False, http_auth=(self.es_user, self.es_pass))
        # add doc
        query = {
            'query': {
                'match': {
                    'tags': tag
                }
            }
        }
        results = []
        for r in es.search(body=query, index=index_name, size=10000)['hits']['hits']:
            data = r['_source']
            meta = data['meta'] if 'meta' in data else {}
            results.append(MetaModel(
                None,
                data['performance'],
                data['description'],
                data['columns_list'],
                data['tags'],
                datetime.strptime(data['creation_date'], '%Y-%m-%dT%H:%M:%S.%f'),
                meta
            ))
        results.sort(key=lambda x: x.creation_date)
        return results


class LocalModelStore(ModelStore):
    """Store pytorch models in a local directory
    """
    def __init__(self, directory : str):
        self.directory = directory
    
    def __generate_path(self, meta_model : MetaModel):
        timestamp = meta_model.creation_date.timestamp()
        tags = '_'.join(meta_model.tags)
        name = f'{tags}_{timestamp}'
        return f'{self.directory}/{name}'

    
    def store(self, meta_model : MetaModel):
        # create dir if needed
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        path = self.__generate_path(meta_model)
        torch.save(meta_model.model, path)
        path = self.__generate_path(meta_model)
        torch.save(meta_model.model, path)
        
        
    def get(self, meta_model : MetaModel) -> list:
        path = self.__generate_path(meta_model)
        return torch.load(path)

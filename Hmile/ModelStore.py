import os
from datetime import datetime
from unittest import result
import torch
from torch import nn
from abc import abstractmethod
from elasticsearch import Elasticsearch

class MetaModel:
    def __init__(self,
            model: nn.Module,
            performance: float,
            description: str,
            columns_list: list,
            tags : list,
            creation_date  : datetime = None):
            """Create a MetaModel object. This objet is used to store the model and to get it back from a model store.
                model (nn.Module): The model to store.
                performance (float): A arbitrary number to describe the performance of the model between 0 and 1.
                description (str): A concise description of the model.
                columns_list (list): An ordered list of the columns used to train the model.
                tags (list) : Keywords to describe the model. Can be use to filter the model store.
                creation_date (_type_, optional): _description_. Defaults to now
            """
            self.model = model
            self.performance = performance
            self.description = description
            self.columns_list = columns_list
            self.tags = tags
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
                'creation_date' : self.creation_date
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
        """Get back a meta objects

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
        """Store a model

        Args:
            meta_model (MetaModel): MetaModel object to store
        """
        raise NotImplementedError()
    
    @abstractmethod
    def get(self, meta_model : MetaModel):
        """Get back a meta objects

        Args:
            meta_model (str): meta_model to get the model back

        """
        raise NotImplementedError()

class ElasticMetaModelStore(MetaModelStore):
    """Store meta models information in ElasticSearch
    """
    def __init__(self, es_url : str, es_user : str, es_pass : str):
        self.es_url = es_url
        self.es_user = es_user
        self.es_pass = es_pass
    
    def store(self, meta_model : MetaModel):
        index_name = 'models'
        es = Elasticsearch(self.es_url, http_compress=True, verify_certs=False, http_auth=(self.es_user, self.es_pass))
        # add doc
        es.index(index=index_name, document=meta_model.__dict__())
    
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
        for r in es.search(body=query, index=index_name)['hits']['hits']:
            data = r['_source']
            results.append(MetaModel(
                None,
                data['performance'],
                data['description'],
                data['columns_list'],
                data['tags'],
                data['creation_date']
            ))
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
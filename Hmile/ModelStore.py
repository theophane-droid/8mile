from typing import Union, List
import pickle
import time
from datetime import datetime
from torch import nn
from abc import abstractmethod
from elasticsearch import Elasticsearch
import base64

class MetaModel:
    """
    This objet is used to store the model and to get it back from a model store. It also stores meta informations about the model.
    
    :ivar model: the pytorch model. Can be None if no model is associated with the MetaModel
    :ivar performance: an arbitrary number between 0 and 1 to describe the performance of the model 
    :ivar description: a concise description of the model
    :ivar columns_list: an ordered list of the columns used to train the model
    :ivar tags: keywords to describe the model. This is the key value to search a MetaModel from a MetaModelStore
    :ivar creation_date: the datetime object when the model was created
    :ivar meta: a dict object to store any other information about the model
    """
    def __init__(self,
            model: Union[nn.Module, str],
            performance: float,
            description: str,
            columns_list: List[str],
            tags : List[str],
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
            if isinstance(model, str):
                data = base64.decodebytes(model.encode('utf-8'))
                self.model = pickle.loads(data)
            elif isinstance(model, nn.Module):
                self.model = model
            else:
                raise TypeError('model must be a str base64 or a nn.Module')
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
        model_data = pickle.dumps(self.model)
        model_b64 = base64.b64encode(model_data).decode('utf-8')
        return {
                'performance' : self.performance,
                'description' : self.description,
                'columns_list' : self.columns_list,
                'tags' : self.tags,
                'creation_date' : self.creation_date,
                'meta' : self.meta,
                'model' : model_b64
        }

class ModelStore:
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
    def get(self, **kwargs) -> List[MetaModel]:
        """Get back a list of meta objects, corresponding to the tag. Each meta model which contains this tag once will be returned.

        Args:
            kwargs (dict): A dict of values to filter the model store. Exemple : {'tag' : 'my_tag', 'performance' : 0.8} will return all the models with the tag 'my_tag' AND a performance of 0.8

        """
        raise NotImplementedError()

class ElasticModelStore(ModelStore):
    """Store meta models information in ElasticSearch in the index 'models'
    """
    def __init__(self, es_url : str, es_user : str, es_pass : str):
        self.es_url = es_url
        self.es_user = es_user
        self.es_pass = es_pass
    
    def store(self, meta_model : MetaModel):
        """Store a MetaModel object in elasticsearch in the index 'models'. If the index does not exist, it will be created.

        Args:
            meta_model (MetaModel): MetaModel object to store
        """
        index_name = 'models'
        es = Elasticsearch(self.es_url, http_compress=True, verify_certs=False, http_auth=(self.es_user, self.es_pass))
        data = meta_model.__dict__()
        es.index(index=index_name, document=data, refresh=True)
        es.close()
        
    def __search(self, index_name, query, limit=10000, search_after=None):
        """Search **query** in **index_name**. If results > **limit**, we split the query in two and search recursively. 

        Args:
            index_name (str) : The elasticsearch index to search
            query (dict): an elastic formatted query
            limit (int, optional): The maximum number of results to return, max to 10000. Defaults to 10000.
            search_after (list, optional): The search_after parameter to paginate the results. Defaults to None.
        """
        print(query)
        query['size'] = limit
        query['sort'] = [{'creation_date' : 'asc'}]
        if search_after:
            query['search_after'] = [search_after]
        es = Elasticsearch(self.es_url, http_compress=True, verify_certs=False, http_auth=(self.es_user, self.es_pass))
        res = es.search(index=index_name, body=query)['hits']['hits']
        nb_results = len(res)
        print('nb_results : ', nb_results)
        if nb_results >= limit:
            return res + self.__search(index_name, query, limit=limit, search_after=res[-1]['_source']['creation_date'])
        return res

    def get(self, limit=10000, **kwargs) -> List[MetaModel]:
        """Return a list of MetaModel objects, corresponding to the keyword arguments. Each meta model which match to each keyword arguments will be returned.
           Arguments can be :
            - performance : float
            - description : str
            - columns_list : List[str]
            - tags : List[str]
            - creation_date : datetime
           
        Args:
            limit (int, optional): number of Elasticsearch results per pagination. Defaults to 10000.

        Raises:
            Exception: if the argument is not in the list of allowed arguments

        Returns:
            List[MetaModel]: the requested list of MetaModel objects
        """
        for key in kwargs.keys():
            if key not in ['tag', 'performance', 'description', 'columns_list', 'tags', 'creation_date']:
                raise Exception(f'Key {key} is not a supported key to filter the model store')
        index_name = 'models'
        query = {
            "query" : {
                "bool" : {
                    "must" : []
                }
            }
        }
        for key, value in kwargs.items():
            query['query']['bool']['must'].append({"match" : {key : value}})
        
        # we search in the index
        res = self.__search(index_name, query, limit=limit)
        # we create a list of MetaModel objects
        meta_model_list = []
        for hit in res:
            meta_model_list.append(MetaModel(
                hit['_source']['model'],
                hit['_source']['performance'],
                hit['_source']['description'],
                hit['_source']['columns_list'],
                hit['_source']['tags'],
                datetime.strptime(hit['_source']['creation_date'], '%Y-%m-%dT%H:%M:%S.%f'),
                hit['_source']['meta']
            ))
        meta_model_list.sort(key=lambda x: x.creation_date)
        return meta_model_list

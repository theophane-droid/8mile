Model store
===========

Hmile provides the ability to store and retrieve torch models. To do that we have built three base classes : 

* MetaModel : model informations like name, description, performance, tags, etc.
* ModelStore : a store for torch models

MetaModel
~~~~~~~~~

.. autoclass:: Hmile.ModelStore.MetaModel
   :members:
   :inherited-members:

ModelStore
~~~~~~~~~~~~~~

.. autoclass:: Hmile.ModelStore.ElasticModelStore
   :members:
   :inherited-members:

Example
~~~~~~~

This can be used to store a model an its meta model as follow :

.. code-block:: python

    from torch import nn
    from Hmile.ModelStore import MetaModel, ElasticModelStore

    ELASTIC_URL = "https://myelastic.com:9200"
    ELASTIC_USER = "myuser"
    ELASTIC_PASSWORD = "mypassword"

    # we create an example model
    model = nn.Sequential(
        nn.Linear(10 , 20)   
    )

    # we create a MetaModel object
    meta = MetaModel(
        model, # the torch model
        0.5, # the model performance
        'test', # the model description
        ['a', 'b', 'c'], # the columns list used to train the model
        ['test'] # the tags
    )

    # we create a MetaModelStore object
    meta_model_store = ElasticModelStore(
        ELASTIC_URL,
        ELASTIC_USER,
        ELASTIC_PASSWORD)

    # then we store our mode_model in it
    meta_model_store.store(meta)

    # we can create a now model storer
    self.storer = LocalModelStore('my/models/path')
    self.storer.store(meta)


Then we can retrieve our model :

.. code-block:: python

    from Hmile.ModelStore import ElasticModelStore

    ELASTIC_URL = "https://myelastic.com:9200"
    ELASTIC_USER = "myuser"
    ELASTIC_PASSWORD = "mypassword"

    # we create a MetaModelStore object
    meta_model_store = ElasticModelStore(
        ELASTIC_URL,
        ELASTIC_USER,
        ELASTIC_PASSWORD)

    # we retrieve the list of models with the tag 'test'
    meta_model_list = meta_model_store.get(tags='test')

    # we now get the model
    model = meta_model_list[-1].model

    # we can now use our model
    model(torch.rand(10))
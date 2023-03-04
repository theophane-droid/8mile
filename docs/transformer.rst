Data transformer
================

A data transformer allow you to apply changes on data. It can be used to add financial indicators, remove indicators, or compress columns.

TaDataTransformer
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: hmile.DataTransformer.TaDataTransformer
   :members:
   :inherited-members:

Check the `ta lib documentation <https://ta-lib.org/>`_ for more information.	

**Examples :**

.. code-block:: python

   from hmile.DataProvider import YahooDataProvider
   from hmile.DataTransformer import TaDataTransformer

   PAIR = "BTCUSD"
   START = "2022-01-01"
   END = "2022-01-03"
   INTERVAL = "hour"

   dp = YahooDataProvider([PAIR], START, END, interval=INTERVAL) 

   # We first need a source of data = a data provider
   data_provider = YahooDataProvider()
   # Create a data transformer
   transformer = TaDataTransformer(data_provider)
   # transform the data
   data = transformer.transform()

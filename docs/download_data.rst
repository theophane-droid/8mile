Download data
=============

For now hmile provide three ways to download the data:

* **yahoofinance** : a reliable source, which contains a lot of assets. However YF contains inconsistencies in volume data
* **polygon.io** : Good data provider, however it is not free
* **csv** : a csv file containing the data, it's efficient but it is not updated. 
* **elasticsearch** : a elasticsearch database containing the data. You have a full control on data but you need to maintains and update it yourself. `See <https://www.elastic.co/fr/what-is/elasticsearch>`_  

All DataProvider provide a method named ``getData`` which returns a dictionnary of a pandas DataFrame. Each key is a name of a requested pair. Exemple :

.. code-block:: json

   {
      "BTCUSD": pd.DataFrame 1,
      "ETHUSD" pd.DataFrame 2
   }



The dataframes are formatted like that.

.. list-table:: data
   :widths: 25 25 25 25 25 25 
   :header-rows: 1

   * - date (index)
     - open
     - high
     - low
     - close
     - volume
   * - 2015-01-08
     - 11.01
     - 10.81
     - 11.30
     - 10.75
     - 1433300
   * - 2015-01-09
     - 10.96
     - 10.98
     - 11.18
     - 10.72
     - 18536300

Yahoofinance
~~~~~~~~~~~~~~~

.. autoclass:: Hmile.DataProvider.YahooDataProvider
   :members:

**Example :**

.. code-block:: bash

   from Hmile.DataProvider import YahooDataProvider
   
   PAIR = "BTCUSD"
   START = "2022-01-01"
   END = "2022-01-03"
   INTERVAL = "hour"

   dp = YahooDataProvider([PAIR], START, END, interval=INTERVAL)
   data = dp.getData()[PAIR]

Polygon.io
~~~~~~~~~~~~~

.. autoclass:: Hmile.DataProvider.PolygonDataProvider
   :members:

**Example :**

.. code-block:: bash

   from Hmile.DataProvider import PolygonDataProvider        
   
   PAIR = "BTCUSD"
   START = "2022-01-01"
   END = "2022-01-03"
   API_KEY = "YOUR_API_KEY"
   INTERVAL = "hour"

   dp = PolygonDataProvider([PAIR], START, END, API_KEY, interval=INTERVAL)
   data = dp.getData()[PAIR]

CSV
~~~~~~

.. autoclass:: Hmile.DataProvider.CSVDataProvider
   :members:

**Example :**

.. code-block:: bash

   from Hmile.DataProvider import CSVDataProvider        
   
   PAIR = "BTCUSD"
   START = "2022-01-01"
   END = "2022-01-03"
   DATA_DIR = "mydata/"
   INTERVAL = "hour"

   dp = CSVDataProvider([PAIR], START, END, DATA_DIR, interval=INTERVAL)
   data = dp.getData()[PAIR]

**Remark :**

The csv file must be named f-{pair}-{interval}.csv and present in the directory DATA_DIR. The csv file must contain the following columns : date, open, high, low, close, volume.

Elasticsearch
~~~~~~~~~~~~~~~~

.. autoclass:: Hmile.DataProvider.ElasticDataProvider
   :members:

**Example :**

.. code-block:: bash

   from Hmile.DataProvider import ElasticDataProvider    
   
   PAIR = "BTCUSD"
   START = "2022-01-01"
   END = "2022-01-03"
   ELASTIC_URL = "https://myelastic.com:9200" # the port must be specified
   ELASTIC_USER = "myuser"
   ELASTIC_PASSWORD = "mypassword"
   INTERVAL = "hour"

   dp = ElasticDataProvider([PAIR], START, END, ELASTIC_URL, ELASTIC_USER, ELASTIC_PASSWORD, interval=INTERVAL)
   data = dp.getData()[PAIR]
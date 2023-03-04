Data exporter
=============

hmile provides the ability to export financial data to csv or elasticsearch.

CSVDataExporter
~~~~~~~~~~~~~~~~~~

.. autoclass:: hmile.Csvexporter
   :members:
   :inherited-members:

**Example :**

.. code-block:: python

   from hmile import Yahooprovider
   from hmile import Csvexporter

   PAIR = "BTCUSD"
   START = "2022-01-01"
   END = "2022-01-03"
   INTERVAL = "hour"
   OUTPUT_DIR = "my/output/dir"

   # We first need a source of data = a data provider
   dp = Yahooprovider([PAIR], START, END, interval=INTERVAL) 

   # Then we creat the exporter
   csv_exporter = Csvexporter(dp, OUTPUT_DIR)

   # Export data to csv
   csv_exporter.export()

ElasticDataExporter
~~~~~~~~~~~~~~~~~~~

.. autoclass:: hmile.Elasticexporter
   :members:
   :inherited-members:

**Example :**

.. code-block:: python

   from hmile import Yahooprovider
   from hmile import Elasticexporter

   PAIR = "BTCUSD"
   START = "2022-01-01"
   END = "2022-01-03"
   INTERVAL = "hour"
   ELASTIC_URL = "https://myelastic.com:9200" # the port must be specified
   ELASTIC_USER = "myuser"
   ELASTIC_PASSWORD = "mypassword"

   # We first need a source of data = a data provider
   dp = Elasticexporter([PAIR], START, END, interval=INTERVAL) 

   # Create a ElasticDataExporter object
   csv_exporter = Elasticexporter(
    dp,
    ELASTIC_URL,
    ELASTIC_USER,
    ELASTIC_PASSWORD
   )

   # Export data to csv
   csv_exporter.export()
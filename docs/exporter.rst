Data exporter
=============

Hmile provides the ability to export financial data to csv or elasticsearch.

1. CSVDataExporter
~~~~~~~~~~~~~~~~~~

.. autoclass:: Hmile.DataExporter.CSVDataExporter
   :members:

**Example :**

.. code-block:: python

   from Hmile.DataProvider import YahooDataProvider
   from Hmile.DataExporter import CSVDataExporter

   PAIR = "BTCUSD"
   START = "2022-01-01"
   END = "2022-01-03"
   INTERVAL = "hour"
   OUTPUT_DIR = "my/output/dir"

   dp = YahooDataProvider(PAIR, START, END, interval=INTERVAL) 

   # We first need a source of data = a data provider
   data_provider = YahooDataProvider()
   # Create a CSVDataExporter object
   csv_exporter = CSVDataExporter(data_provider, OUTPUT_DIR)

   # Export data to csv
   csv_exporter.export()

2. ElasticDataExporter
~~~~~~~~~~~~~~~~~~

.. autoclass:: Hmile.DataExporter.ElasticDataExporter
   :members:

**Example :**

.. code-block:: python

   from Hmile.DataProvider import YahooDataProvider
   from Hmile.DataExporter import ElasticDataExporter

   PAIR = "BTCUSD"
   START = "2022-01-01"
   END = "2022-01-03"
   INTERVAL = "hour"
   ELASTIC_URL = "https://myelastic.com:9200" # the port must be specified
   ELASTIC_USER = "myuser"
   ELASTIC_PASSWORD = "mypassword"

   dp = ElasticDataExporter(PAIR, START, END, interval=INTERVAL) 

   # We first need a source of data = a data provider
   data_provider = YahooDataProvider()
   # Create a ElasticDataExporter object
   csv_exporter = ElasticDataExporter(
    data_provider,
    ELASTIC_URL,
    ELASTIC_USER,
    ELASTIC_PASSWORD
   )

   # Export data to csv
   csv_exporter.export()
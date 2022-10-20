Welcome to 8mile-render's documentation!
========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

8mile is a module to treat financial data for machine learning purpose.

Quickstart
---------------

First we need to install ta-lib which 8Mile use for technical indicator calculation.

.. code-block:: bash

   wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
   tar -xzf ta-lib-0.4.0-src.tar.gz
   cd ta-lib/ && ./configure --prefix=/usr && make && make install

It could take a moment to compile. Then, install 8mile with:

.. code-block:: bash
   
   pip3 install hmile


First usage
-----------

We can begin with a simple usage of 8mile by downlading bitcoin data from yahoofinance.

.. code-block:: python3
   
   from hmile.DataProvider import YahooDataProvider
   from hmile.FillPolicy import FillPolicyAkima

   PAIR = "BTCUSD"
   START = "2022-01-01"
   END = "2022-01-03"
   INTERVAL = "hour"

   dp = YahooDataProvider(PAIR, START, END, interval=INTERVAL)
   # used to fill eventual missing dates (optionnal)
   dp.fill_policy = FillPolicyAkima(INTERVAL)

   data = dp.getData()

Here we use the Akima fill policy, it allows us to fill missing dates by interpolate between known values.

Lets continue
-------------

To continue with hmile :

.. toctree::
   download_data.rst
   fix_data.rst
   renderer.rst
   exporter.rst
   transformer.rst
   modelstore.rst
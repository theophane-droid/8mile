Fix data
========

In some data providers there could be holes in the data. For various reasons somes dates could be missing in your data. 
For exemple what can you do if your data looks like : 

.. list-table:: data
   :widths: 25 25 25 25 25 25 
   :header-rows: 1

   * - date
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
   * - 2015-01-12
     - 11.06
     - 11.32
     - 11.42
     - 10.88
     - 31410200
   * - 2015-01-13
     - 11.47
     - 10.68
     - 11.48
     - 10.52
     - 27751100

The module FillPolicy helps you to fill the missing dates. By default if you don't choose a fill policy, if hmile detects missing dates it will raises a **NoFillPolicySet** exception.

FillPolicyAkima
~~~~~~~~~~~~~~~~~~
.. autoclass:: hmile.FillPolicy.FillPolicyAkima
   :members:

**Example :**

.. code-block:: python

    from hmile.FillPolicy import FillPolicyAkima
    from hmile.DataProvider import CSVDataProvider

    # Create a data provider
    data_provider = CSVDataProvider([PAIR], START, END, DATA_DIR, interval=INTERVAL)
    # We set the fill policy
    data_provider.fill_policy = FillPolicyAkima(INTERVAL)
    # We get the data, the fill policy will be applied automatically
    data = fill_policy.get_data()

**Remark :**

The FillPolicyAkima class is based on the Akima interpolation method. So missing data will be generated from a statistical method.

FillPolicyClip
~~~~~~~~~~~~~~~~~
.. autoclass:: hmile.FillPolicy.FillPolicyClip
   :members:

**Example :**

.. code-block:: python

    from hmile.FillPolicy import FillPolicyClip
    from hmile.DataProvider import CSVDataProvider

    # Create a data provider
    data_provider = CSVDataProvider([PAIR], START, END, DATA_DIR, interval=INTERVAL)
    # We set the fill policy
    data_provider.fill_policy = FillPolicyClip(INTERVAL)
    # We get the data, the fill policy will be applied automatically
    data = fill_policy.get_data()

**Remark :**
This method will just ignore if there is missing data.

FillPolicyError
~~~~~~~~~~~~~~~~~~

.. autoclass:: hmile.DataProvider.FillPolicyError
   :members:

**Example :**

.. code-block:: python

    from hmile.FillPolicy import FillPolicyError
    from hmile.DataProvider import CSVDataProvider

    # Create a data provider
    data_provider = CSVDataProvider([PAIR], START, END, DATA_DIR, interval=INTERVAL)
    # We set the fill policy
    data_provider.fill_policy = FillPolicyError(INTERVAL)
    # We get the data, the fill policy will be applied automatically
    data = fill_policy.get_data()

**Remark :**
If there is missing data, this fill policy will raised an exception. This is the default fill policy.

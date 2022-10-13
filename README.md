# 8 MILE

[![Build](https://github.com/theophane-droid/8mile/actions/workflows/python-test-publish.yml/badge.svg)](https://github.com/theophane-droid/8mile/actions/workflows/python-test-publish.yml/badge.svg) [![Documentation](https://readthedocs.org/projects/8mile/badge/?version=latest)](https://8mile.readthedocs.io/en/latest/?badge=latest) 

Python 3.x module to treat financial data. Many features including :
* download financial data from various sources
* preprocess data
* export data
* plot data in tensorboard

![](img/8mile.jpg)

## Installation 🔥

Pre-requisites:
- python3
- pip3

Install the talib library:

```bash
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/ && ./configure --prefix=/usr && make && make install
```

Install the package with pip3

```bash
pip3 install hmile
```

## Usage 🚀

Simple example do download yahoo data and apply all ta features to it.

```python
PAIR = "BTCUSD"
START = "2021-12-01"
END = "2022-05-24"
INTERVAL = "hour"

PATH = 'output/csvdataexporter'


yf_dp = YahooDataProvider(PAIR, START, END, interval=INTERVAL)
data = TaFeaturesTransformer(yf_dp).transform()
print(data.tail(10))
```

Using tensorboard plotting with RabbitRenderer


```python
from datetime import datetime
import pandas as pd
from Hmilerender.RabbitRenderer import RabbitRenderer

def fill_renderer(data, renderer):
 # we fill the renderer with data rows
   for index, row in data.iterrows():
      date = datetime.strptime(row["Date"], "%Y-%m-%d")
      renderer.append("open", row["open"], date)
      renderer.append("close", row["close"], date)
      renderer.append("high", row["high"], date)
      renderer.append("low", row["low"], date)
      renderer.append("volume", row["volume"], date)
      renderer.append("exit", row["exit"], date)
      renderer.append("long", row["long"], date)
      renderer.append("short", row["short"], date)
      renderer.append("money", row["money"], date)

# we create a renderer object
renderer = RabbitRenderer('logs/')
# we read data
data = pd.read_csv('data/data.csv')
# we fill renderer
fill_renderer(data, renderer)
# we launch renderer
renderer.render()
# then we increment tensorboard step
renderer.next_step()
# we refill the renderer
fill_renderer(data, renderer)
# we launch renderer
renderer.render()
```

## Build doc 🛠️

You can rebuild the doc with the following commands:

```bash
make html
rm -r docs
mv _build/html docs
rm -rf _build
```

## Documentation 📚

[Find doc here](https://8mile.readthedocs.io/en/latest/index.html#Hmile.DataProvider.CSVDataProvider)


## Launch tests 🧪

Please ensure you have installed [docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/).

First build the docker image:

```bash
docker compose build
```

Then start the containers :

```bash
docker compose up -d
```

Then run the tests :

```bash
docker compose run --rm tester python3 /app/test/test_dataexporter.py
docker compose run --rm tester python3 /app/test/test_dataprovider.py
docker compose run --rm tester python3 /app/test/test_datatransformer.py
```
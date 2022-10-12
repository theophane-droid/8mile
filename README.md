# 8 MILE RENDER

Python 3.x module to treat time series data espacially financial ones.

Actual version : 0.2.1

![](img/8mile.jpg)


## Installation 🔥

Pre-requisites:
- ta-lib
- python3
- pip3

Install the package with pip3
```bash
pip3 install git+https://github.com/theophane-droid/8miles-render
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

[Find doc here](https://theophane-droid.github.io/8miles-render/)


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
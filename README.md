# 8 MILE RENDER

Python 3.x module to treat time series data espacially financial ones.

Actual version : 0.1.0

## Installation 🔥

Pre-requisites:
- ta-lib
- python3
- pip3

```bash
pip3 install git+https://github.com/theophane-droid/8miles-render
```

## Build doc 📚

```bash
make html
rm -r docs
mv _build/html docs
rm -rf _build
```

## Documentation 📚

[Find doc here](https://theophane-droid.github.io/8miles-render/)

![](img/8mile.jpg)

## Launch tests 🧪

Please ensure to have installer [docker](https://docs.docker.com/get-docker/) and [docker-compose](https://docs.docker.com/compose/install/).

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
docker compose run --rm tester python3 /app/scripts/test_dataexporter.py
```
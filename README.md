# 8 MILE RENDER

Python 3.x module to render time series data espacially finantial ones.

Actual version : 0.1.0

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
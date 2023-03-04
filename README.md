# 8 MILE

[![Test](https://github.com/theophane-droid/8mile/actions/workflows/python_test.yml/badge.svg)](https://github.com/theophane-droid/8mile/actions/workflows/python_test.yml/badge.svg) [![Documentation](https://readthedocs.org/projects/8mile/badge/?version=latest)](https://8mile.readthedocs.io/en/latest/?badge=latest)

Python 3.x module to treat financial data for machine learning purpose. Many features including :
* download financial data from various sources
* preprocess data
* export data

![](img/8mile.jpg)

## 🔥 Installation

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

## 📚 Documentation

[Find doc here](https://8mile.readthedocs.io/en/latest)

## 🛠️ Build doc

You can rebuild the doc with the following commands:

```bash
make html
rm -r docs
mv _build/html docs
rm -rf _build
```
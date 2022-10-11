import sys
from datetime import datetime, timedelta
import pytz
import os

sys.path.insert(0, '/app')

from Hmile.DataProvider import YahooDataProvider
from Hmile.DataTransformer import TaFeaturesTransformer

PAIR = "BTCUSD"
START = "2021-12-01"
END = "2022-05-24"
INTERVAL = "hour"
ES_URL = "https://elastic:9200"
ES_USER = "elastic"
ES_PASS = "changeme"

PATH = '/output/csvdataexporter'

if __name__ == "__main__":
    yf_dp = YahooDataProvider(PAIR, START, END, interval=INTERVAL)
    data = TaFeaturesTransformer(yf_dp).transform()
    print(data.tail(10))
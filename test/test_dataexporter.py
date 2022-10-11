import sys
from datetime import datetime, timedelta
import pytz
import os

sys.path.insert(0, '/app')

from Hmile.DataProvider import YahooDataProvider
from Hmile.DataExporter import CSVDataExporter, ElasticDataExporter

PAIR = "BTCUSD"
START = "2021-12-01"
END = "2022-05-24"
INTERVAL = "hour"
ES_URL = "https://elasticsearch:9200"
ES_USER = "elastic"
ES_PASS = "changeme"

PATH = '/output/csvdataexporter'

if __name__ == "__main__":
    os.mkdir('/output')
    os.mkdir(PATH)
    yf_dp = YahooDataProvider(PAIR, START, END, interval=INTERVAL)
    CSVDataExporter(yf_dp, PATH).export()
    ElasticDataExporter(yf_dp, ES_URL, ES_USER, ES_PASS).export()
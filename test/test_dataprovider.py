import sys
from datetime import datetime, timedelta
import pytz

sys.path.insert(0, '/app')

from Hmile.DataProvider import CSVDataProvider, ElasticDataProvider, YahooDataProvider
from Hmile.DataExporter import CSVDataExporter
from Hmile.FillPolicy import FillPolicyAkima

interval_to_timedelta = {
    'minute': timedelta(minutes=1),
    'hour': timedelta(hours=1),
    'day': timedelta(days=1),
}

def test_dataprovider(dataprovider, start_date, end_date, interval):
    print(f'**** TESTING {dataprovider.__class__.__name__} ****')
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    data = dataprovider.getData()
    print(data.head())
    assert data is not None
    first = data.index[0].to_pydatetime()
    first =  first.replace(tzinfo=pytz.utc)
    start = start.replace(tzinfo=pytz.utc)
    last = data.index[-1].to_pydatetime()
    last = last.replace(tzinfo=pytz.utc)
    end = end.replace(tzinfo=pytz.utc)
    second = data.index[1].to_pydatetime()
    second = second.replace(tzinfo=pytz.utc)
    assert first == start
    assert last == end
    assert second - first == interval_to_timedelta[interval]

PAIR = "BTCUSD"
START = "2022-01-01"
END = "2022-01-03"
INTERVAL = "hour"
ES_URL = "https://elastic:9200"
ES_USER = "elastic"
ES_PASS = "changeme"

if __name__ == "__main__":
    csv_dp = CSVDataProvider(PAIR, '2021-12-01', END, "test/data/csvdataprovider", interval=INTERVAL)
    csv_dp.fill_policy = FillPolicyAkima(INTERVAL)
    yfinance_dp = YahooDataProvider(PAIR, START, END, interval=INTERVAL)
    elastic_dp = ElasticDataProvider(PAIR, START, END, ES_URL, ES_USER, ES_PASS, interval=INTERVAL)
    test_dataprovider(yfinance_dp, START, END, INTERVAL)
    test_dataprovider(csv_dp, '2021-12-01', END, INTERVAL)
    test_dataprovider(elastic_dp, START, END, INTERVAL)
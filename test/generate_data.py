import argparse

import yfinance as yf

import random
import pandas as pd

choices = [True, False, False, False, False]

if __name__ == "__main__":
    # parse arg to get ticker, start date, end date, and output file
    parser = argparse.ArgumentParser()
    parser.add_argument("ticker", help="ticker to download")
    parser.add_argument("--start", help="start date to download", default="2015-01-01")
    parser.add_argument("--end", help="end date to download", default="2015-01-30")
    parser.add_argument("--output", help="output file to save to", default=None)
    args = parser.parse_args()

    # download data
    data = yf.download(args.ticker, args.start, args.end)
    
    pos = False
    exit = []
    short = []
    long = []
    base_money = 100
    money = []

    for i in range(data.shape[0]):
        val = data.iloc[i]['Close']
        if not pos :
            if random.choice(choices):
                pos = True
                exit.append(None)
                short.append(val)
                long.append(None)
            elif random.choice(choices):
                pos = True
                exit.append(None)
                short.append(None)
                long.append(val)
            else :
                exit.append(None)
                short.append(None)
                long.append(None)
        elif random.choice(choices):
            pos = False
            exit.append(val)
            short.append(None)
            long.append(None)
        else:
            exit.append(None)
            short.append(None)
            long.append(None)
        if len(money) == 0:
            money.append(base_money)
        else:
            money.append(money[-1] + random.randint(-5, 10))

    exit = pd.Series(exit, index=data.index)
    short = pd.Series(short, index=data.index)
    long = pd.Series(long, index=data.index)
    money = pd.Series(money, index=data.index)
    data = pd.DataFrame(
        {'open' : data['Open'],
         'close' : data['Close'],
         'high' : data['High'],
         'low' : data['Low'],
         'volume' : data['Volume'],
         'exit' : exit,
         'long' : long,
         'short' : short,
         'money' : money},
        index=data.index)
    data.to_csv(args.output)
import sys
import os
import argparse

import pandas as pd

from datetime import datetime

import sys
sys.path.insert(0, '/home/droid/8miles-render')
from Hmilerender.RabbitRenderer import RabbitRenderer
from random import randint


def fill_renderer(data, renderer, activate_date=True):
    for index, row in data.iterrows():
        # parse date from row["Date"] as YYYY-dd-mm
        if activate_date:
            date = datetime.strptime(row["Date"], "%Y-%m-%d")
        else:
            date = None
        renderer.append("open", row["open"], date)
        renderer.append("close", row["close"], date)
        renderer.append("high", row["high"], date)
        renderer.append("low", row["low"], date)
        renderer.append("volume", row["volume"], date)
        renderer.append("exit", row["exit"], date)
        renderer.append("long", row["long"], date)
        renderer.append("short", row["short"], date)
        renderer.append("money", row["money"], date)
        renderer.append("rew", randint(1,100), date)

if __name__ == "__main__":
    # parse args to get data_path and logs_dir
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", help="path to data file", default='test/data/data.csv')
    parser.add_argument("--logs_dir", help="path to logs directory", default='logs')
    args = parser.parse_args()

    # read data
    data = pd.read_csv(args.data_path)

    # create renderer
    renderer = RabbitRenderer(
        args.logs_dir,
        activate_rew=True
    )
    # fill renderer with data
    fill_renderer(data, renderer)
    # render
    renderer.render()
    
    renderer.next_step()
    
    fill_renderer(data, renderer, activate_date=False)
    
    renderer.render()
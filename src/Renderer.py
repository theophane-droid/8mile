import mplfinance as mpf
import numpy as np
from matplotlib import pyplot as plt
from random import randint
import io
import IPython.display as IPydisplay
import tensorflow as tf
import threading
import numpy as np
import pandas as pd

NoneType = type(None)

DATE_FORMAT = '%d/%m/%y_%H:%M'

from datetime import datetime

class RenderState:
    def __init__(self, name):
        self.str_date = datetime.now().strftime(DATE_FORMAT)
        self.step = 0
        self.name = name
        self.open = np.array([])
        self.close = np.array([])
        self.low = np.array([])
        self.high = np.array([])
        self.volume = np.array([])
        self.long_metric = np.array([])
        self.short_metric = np.array([])
        self.exit_metric = np.array([])
        self.money = np.array([])
    
    def __str__(self):
        return self.name + '_' + self.str_date

def render(ohlcv_df, long=None, short=None, exit=None, money=None, logdir=None):
    apd = []
    if not isinstance(long, NoneType) and not np.isnan(long).all():
        a = mpf.make_addplot(long,type='scatter', marker='^', markersize=100, color='b', panel=0)
        apd.append(a)
    if not isinstance(short, NoneType) and not np.isnan(short).all():
        a = mpf.make_addplot(short,type='scatter', marker='v', markersize=100, color='g', panel=0)
        apd.append(a)
    if not isinstance(exit, NoneType) and not np.isnan(exit).all():
        a = mpf.make_addplot(exit,type='scatter', marker='x', markersize=100, color='r', panel=0)
        apd.append(a)
    if not isinstance(money, NoneType) and np.sum(money) != np.nan:
        a = mpf.make_addplot(money, ylabel='\$\$', markersize=100, color='r', panel=2)
        apd.append(a)
    fig = mpf.figure(style='yahoo',figsize=(10,7))
    ax1 = fig.add_subplot(4,1,1)
    if not(logdir):
        mpf.plot(ohlcv_df, type='line', addplot=apd, volume=True, figsize=(10,7))
    else:
        buf = io.BytesIO()
        mpf.plot(ohlcv_df, type='line', addplot=apd, volume=True, figsize=(10,7), savefig=buf)
        image = tf.image.decode_image(buf.getvalue(), channels=4)
        image = tf.expand_dims(image, 0)
        writer = tf.summary.create_file_writer(logdir)
        with writer.as_default():
            summary_op = tf.summary.image("Training data", image, step=2)
            writer.flush()

class RenderThread(threading.Thread):
    def __init__(self,
                ohlcv_df : pd.Dataframe,
                renderstate : RenderState,
                long=None,
                short=None,
                exit=None,
                money=None,
                logdir=None):
        threading.Thread.__init__(self) 
        self.ohlcv_df = ohlcv_df
        self.long = long
        self.short = short
        self.exit = exit
        try:
            self.money = money.cpu().numpy()
        except:
            self.money = money
        self.logdir = logdir

    def run(self):
        render(self.ohlcv_df, self.long, self.short, self.exit, self.money, self.logdir)
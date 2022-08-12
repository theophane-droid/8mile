from datetime import datetime, timedelta
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

from random import randint
from Hmilerender.Renderer import Renderer


additional_params = {
    'short' : {'marker' : 'v', 'color' :'g', 'panel' : 0, 'type' : 'scatter', 'markersize' : 100},
    'long' :  {'marker' : '^', 'color' :'b', 'panel' : 0, 'type' : 'scatter', 'markersize' : 100},
    'exit' :  {'marker' : 'x', 'color' :'r', 'panel' : 0, 'type' : 'scatter', 'markersize' : 100},
    'money' :  {'marker' : 'x', 'color' :'r', 'panel' : 2, 'type' : 'line', 'markersize' : 100, 'ylabel' : '\$\$'},
}


DATE_FORMAT = '%Y-%m-%d_%H:%M:%S'
# ajouter légende
# ajouter nom de la paire
class RabbitRenderer(Renderer):
    """Render in tensorboard
    """
    def __init__(self, 
                 logdir, 
                 name='Rabbit_render', 
                 tags=['rabbit'],
                 activate_volume=False,
                 date_in_name=True):
        """Create a rabbitrenderer

        Args:
            logdir (str): directory to store tensorboard data
            name (str, optional): tensorboard data's name. Defaults to 'Rabbit_render'.
            tags (list, optional): tensorboard tags list. Defaults to ['rabbit'].
            activate_volume (bool, optional): should volume be shown. Defaults to False.
            date_in_name (bool, optional): should the name be shown in tensorboard data's name. Defaults to True.
        """
        super().__init__(
            ['open', 'close', 'low', 'high', 'volume', 'long', 'short', 'exit', 'money'] ,
            threaded=False
        )
        self.logdir = logdir
        self.render_params['step'] = 0
        if date_in_name:
            self.name = name + '_' + datetime.now().strftime(DATE_FORMAT)
        else:
            self.name = name
        self.tags = tags
        self.activate_volume = activate_volume
    
    def render_func(self, render_params : dict):
        selected_cols = {k : v for k, v in self.columns.items() if k in ['open', 'close', 'low', 'high', 'volume']}
        ohlcv = pd.DataFrame(selected_cols)
        
        apd = []
        for key in additional_params.keys():
            col = self.columns[key]
            if not np.isnan(col).all():
                if 'panel' in additional_params[key] and additional_params[key]['panel'] > 1 and \
                      not self.activate_volume:
                    additional_params[key]['panel'] -=1
                a = mpf.make_addplot(col, **additional_params[key])
                apd.append(a)
        fig = mpf.figure(style='yahoo',figsize=(10,7))
        if not(self.logdir):
            mpf.plot(ohlcv, type='line', addplot=apd, volume=True, figsize=(10,7))
        else:
            buf = io.BytesIO()
            mpf.plot(ohlcv, type='line', addplot=apd, volume=self.activate_volume, figsize=(10,7), savefig=buf)
            image = tf.image.decode_image(buf.getvalue(), channels=4)
            image = tf.expand_dims(image, 0)
            writer = tf.summary.create_file_writer(self.logdir)
            with writer.as_default():
                summary_op = tf.summary.image(self.name, image, step=render_params['step'])
                writer.flush()
    
    def next_step(self):
        """Increment the tensorboard step data and reinitialize all column's data
        """
        self.render_params['step'] += 1
        self.init_columns()
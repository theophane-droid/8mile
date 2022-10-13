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
from threading import Thread
import pandas as pd
import copy

from .Exception import ColumnNameDoesNotExists, DataframeFormatException

from random import randint

additional_params = {
    'short' : {'marker' : 'v', 'color' :'g', 'panel' : 0, 'type' : 'scatter', 'markersize' : 100},
    'long' :  {'marker' : '^', 'color' :'b', 'panel' : 0, 'type' : 'scatter', 'markersize' : 100},
    'exit' :  {'marker' : 'x', 'color' :'r', 'panel' : 0, 'type' : 'scatter', 'markersize' : 100},
    'money' :  {'marker' : 'x', 'color' :'r', 'panel' : 3, 'type' : 'line', 'markersize' : 10, 'ylabel' : '\$\$ (red)'},
    'rew' :  {'color' :'b', 'panel' : 2, 'type' : 'line', 'ylabel' : 'rew (blue)'}
}


DATE_FORMAT = '%Y-%m-%d_%H:%M:%S'

class RenderTask(Thread):
    """Render in a Thread
    """
    def __init__(self, func, render_params):
        """Create a render task

        Args:
            func (function): the function to start in thread
            render_params (dict): data to be passed as arguments of func
        """
        Thread.__init__(self)
        self.func = func
        self.render_params = render_params

    def run(self):
        self.func(self.render_params)

class DataRenderer:
    """
    Abstract class to guide the construction of a Renderer. To renderer multi-column, time series data.
    """
    def __init__(
        self,
        data_column_names : list,
        threaded=True
    ) -> None:
        """Create a renderer

        Args:
            data_column_names (list): the attributes name of time series data
            threaded (bool, optional): should the render method be started in a thread. Defaults to True.
        """
        self.columns_names = data_column_names
        self.threaded = threaded
        self.render_task = None
        self.init_columns()
        self.render_params = {}
        
    def init_columns(self):
        """Initialize column as empty pd.Series
        """
        self.columns = {
            col : pd.Series(dtype='float') for col in self.columns_names
        }
    
    def append(self,
               column_name : str,
               value : object,
               date : datetime = None) -> None:
        """Append a value to a column

        Args:
            column_name (str): column to select
            value (object): value to append
            date (datetime, optional): date for value. Defaults to None.

        Raises:
            ColumnNameDoesNotExists: raised if column_name does not exists in renderer
        """
        if date == None:
            date = datetime(2000, 8, 3) + timedelta(days=self.columns[column_name].shape[0])
        if column_name in self.columns :
            s = pd.Series([value], dtype='float', index=[date])
            self.columns[column_name] = pd.concat(
                [self.columns[column_name], s])
        else:
            raise ColumnNameDoesNotExists(column_name)
    
    def render_func(self, render_params : dict) -> None:
        """Implement here the rendering method. This method should not be called. Use render method

        Args:
            render_params (dict): parameters that should be passed to the thread

        Raises:
            NotImplemented: the function should be implemented
        """
        raise NotImplemented()
    
    def render(self):
        """Launch the rendering of all appended data
        """
        if self.threaded :
            if self.render_task:
                self.render_task.join(timeout=0.1)
            task = RenderTask(self.render_func, copy.deepcopy(self.render_params))
            self.render_task = task.start()
        else:
            self.render_func(copy.deepcopy(self.render_params))

class TensorboardDataRenderer(DataRenderer):
    """Render in tensorboard
    Show open, high, low, close, volume and can show money, reward, short signals, long signals, and exit signals
    """
    def __init__(self, 
                 logdir, 
                 name='Rabbit_render', 
                 tags=['rabbit'],
                 activate_volume=False,
                 activate_rew=False,
                 date_in_name=True):
        """Create a rabbitrenderer

        Args:
            logdir (str): directory to store tensorboard data
            name (str, optional): tensorboard data's name. Defaults to 'Rabbit_render'.
            tags (list, optional): tensorboard tags list. Defaults to ['rabbit'].
            activate_volume (bool, optional): should volume be shown. Defaults to False.
            activate_rew (bool, optional): should reward be shown. Defaults to False.
            date_in_name (bool, optional): should the name be shown in tensorboard data's name. Defaults to True.
        """
        super().__init__(
            ['open', 'close', 'low', 'high', 'volume', 'long', 'short', 'exit', 'money', 'rew'] ,
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
        # check if all the selected_cols have the same length
        for i in selected_cols.keys():
            for j in selected_cols.keys():
                if selected_cols[i].shape[0] != selected_cols[j].shape[0]:
                    raise DataframeFormatException('All columns in open, close, low, high and volume should have the same length to render', None)
        ohlcv = pd.DataFrame(selected_cols)
        
        apd = []
        for key in additional_params.keys():
            col = self.columns[key]
            if not np.isnan(col).all() and self.columns[key].shape[0] > 0:
                if 'panel' in additional_params[key] and additional_params[key]['panel'] > 1 and \
                      not self.activate_volume:
                    additional_params[key]['panel'] -=1
                a = mpf.make_addplot(col, **additional_params[key])
                apd.append(a)
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
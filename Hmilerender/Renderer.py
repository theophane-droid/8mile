from datetime import datetime, timedelta
from threading import Thread
import pandas as pd
import copy

from .Exception import ColumnNameDoesNotExists

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

class Renderer:
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
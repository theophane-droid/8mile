from datetime import datetime, timedelta
from threading import Thread
import pandas as pd
import copy

from .Exception import ColumnNameDoesNotExists

class RenderTask(Thread):
    """Render in a Thread
    """
    def __init__(self, func, render_params):
        Thread.__init__(self)
        self.func = func
        self.render_params = render_params

    def run(self):
        self.func(self.render_params)

class Renderer:
    """
    Abstract class to guide the construction of a renderer
    """
    def __init__(
        self,
        data_column_names : list,
        threaded=True
    ) -> None:
        """Create a Renderer

        Args:
            data_column_names (dict): data used to render
            threaded (bool, optional): launch in thread. Defaults to True.
        """
        self.columns_names = data_column_names
        self.threaded = threaded
        self.render_task = None
        self.init_columns()
        self.render_params = {}
        
    def init_columns(self):
        self.columns = {
            col : pd.Series(dtype='float') for col in self.columns_names
        }
    
    def append(self,
               column_name : str,
               value : object,
               date : datetime = None) -> None:
        """Append a value to a column

        Args:
            column_name (str): column name
            value (object): the value to add
            date (datetime): date of the observation

        Raises:
            ColumnNameDoesNotExists: if column_name was not been declared when creating Renderer 
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
        """Abstact method which should contains the render 

        Raises:
            NotImplemented: raise if not overwrided
        """
        raise NotImplemented()
    
    def render(self):
        """
        To call to launch the render phase
        """
        if self.threaded :
            if self.render_task:
                self.render_task.join(timeout=0.1)
            task = RenderTask(self.render_func, copy.deepcopy(self.render_params))
            self.render_task = task.start()
        else:
            self.render_func(copy.deepcopy(self.render_params))
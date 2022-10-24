import pandas as pd

class ColumnNameDoesNotExists(Exception):
    """Raised if user try to access to a not existing column in Hmilerender.Renderer.Renderer
    """
    def __init__(self, column_name) -> None:
        super().__init__(self)
        self.column_name = column_name
    
    def __str__(self) -> str:
        return """%s is not an existing data column""" % (self.column_name)
    

class DataframeFormatException(Exception):
    """Raise an exception if the dataframe does not correspond to the Hmile specification.
    """
    def __init__(self, msg : str, dataframe : pd.DataFrame) -> None:
        super().__init__(self)
        self.msg = msg
        self.dataframe = dataframe
    
    def __str__(self) -> str:
        if type(self.dataframe) != type(None):
            return f'{self.msg} : {self.dataframe.head()}'
        else:
            return self.msg


class DataProviderArgumentException(Exception):
    """Raise an exception if the data provider argument is not valid.
    """
    def __init__(self, msg : str) -> None:
        super().__init__(self)
        self.msg = msg
    
    def __str__(self) -> str:
        return f'{self.msg}'


class NoFillPolicySet(Exception):
    """Exception raised when dates are missing in dataframe and no fill policy is set.
    """
    
    def __str__(self) -> str:
        return 'No fill policy set and dates are missing in dataframe. Please set a fill policy like FillPolicyAkima or FillPolicyClip'


class EmptyDataRendererException(Exception):
    """Exception raised when trying to render an empty dataframe.
    """
    
    def __str__(self) -> str:
        return 'You tried to render an empty dataframe. Please check your data'


class DataNotAvailableException(Exception):
    """
    This exception is raised when a dataprovider cannot deliver the data.
    """
    def __init__(self, pair, start_date, end_date) -> None:
        super().__init__(self)
        self.pair = pair
        self.start_date = start_date
        self.end_date = end_date
    
    def __str__(self) -> str:
        return f'Data is not available. Maybe pair {self.pair} does not exist or the date range {self.start_date} - {self.end_date} is not available'
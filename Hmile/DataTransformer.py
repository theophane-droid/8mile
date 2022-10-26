from typing import Dict
from abc import abstractmethod

from datetime import datetime, timedelta
import pandas as pd
import pandas_ta as ta

from Hmile.DataProvider import DataProvider, interval_to_timedelta
from Hmile.ModelStore import ModelStore, ModelStore


class DataTransformer:
    """
    Abstraction class to apply data transformation
    
    :ivar dataprovider: The dataprovider to use to get the data
    """

    def __init__(self, dataprovider : DataProvider) -> None:
        self.dataprovider = dataprovider

    def transform(self) -> Dict[str, pd.DataFrame]:
        """
        Apply transformation. Return a dict of dataframes with the key the pair and the value the corresponding dataframe.
        Every dataframe should have the same columns and the same index : 
        The main columns are named be open, high, low, close, volume. In index is the date.
        The index name is'date'
        
        Returns:
            Dict[str, pd.DataFrame]: The transformed data
        """
        if isinstance(self.dataprovider, DataProvider):
            data = self.dataprovider.getData()
        elif isinstance(self.dataprovider, DataTransformer):
            data = self.dataprovider.transform()
        else:
            raise TypeError('dataprovider not a valid type. Must be DataProvider or DataTransformer')
        
        return {
            pair : self._apply_transform(data[pair]) for pair in data.keys()
        }

    @abstractmethod
    def _apply_transform(self, data : pd.DataFrame) -> pd.DataFrame:
        """Apply transformation to a dataframe. Must be implemented by the child class

        Args:
            data (pd.DataFrame): the normalized dataframe to transform
            
        Returns:
            pd.DataFrame: The transformed dataframe
        """
        raise NotImplementedError()


class TaDataTransformer(DataTransformer):
    """
    Add all technical analysis indicators to the data 
    
    :ivar dataprovider: The dataprovider to use to get the data
    """
    def __init__(self, dataprovider : DataProvider) -> None:
        """Create a new TaDataTransformer
       
        Args:
            dataprovider (Hmile.DataProvider.Dataprovider): Dataprovider to transform
        """
        super().__init__(dataprovider)
        # set dataprovider start date to 50 interval before
        self.initial_start_date = self.dataprovider.start_date
        start_date = datetime.strptime(self.dataprovider.start_date, "%Y-%m-%d")
        start_date = min(
            start_date  - interval_to_timedelta[self.dataprovider.interval] * 100, 
            start_date - timedelta(days=1)
        )
        self.dataprovider.start_date = start_date.strftime("%Y-%m-%d")

    def integrity_for_normalization(self,data : pd.DataFrame) -> pd.DataFrame :
        """drop columns with nans and check that std is not too low to avoid nan during normalizing

        Args:
            data (pd.DataFrame): data to check

        Returns:
            pd.DataFrame: data cleaned up
        """
        data2 = (data-data.mean())/data.std()
        data2.dropna(axis=1,inplace=True)
        data = data[data2.columns]
        return data

    def _apply_transform(self, data : pd.DataFrame):
        data.ta.strategy("all")
        data = data[self.initial_start_date:]
        data = self.integrity_for_normalization(data)
        # returns data from the start_date
        return data

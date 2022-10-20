from abc import abstractmethod

from datetime import datetime, timedelta
import pandas as pd
import pandas_ta as ta

from Hmile.DataProvider import DataProvider, interval_to_timedelta
from Hmile.ModelStore import MetaModelStore, ModelStore


class DataTransformer:
    """Abstraction class to apply data transformation
    """

    def __init__(self, dataprovider : DataProvider) -> None:
        self.dataprovider = dataprovider

    def transform(self):
        """Apply transformation
        """
        if isinstance(self.dataprovider, DataProvider):
            return self.apply_transform(self.dataprovider.getData())
        elif isinstance(self.dataprovider, DataTransformer):
            return self.apply_transform(self.dataprovider.transform())
        else:
            raise TypeError('dataprovider not a valid type. Must be DataProvider or DataTransformer')
        
    @abstractmethod
    def apply_transform(self, data : pd.DataFrame):
        raise NotImplementedError()


class TaDataTransformer(DataTransformer):
    def __init__(self, dataprovider : DataProvider) -> None:
        """Apply all technical analysis features to the data

        Args:
            dataprovider (Hmile.DataProvider.Dataprovider): Dataprovider to transform
            ta_features (list): list of technical analysis features to apply
        """
        super().__init__(dataprovider)
        # set dataprovider start date to 50 interval before
        self.initial_start_date = self.dataprovider.start_date
        start_date = datetime.strptime(self.dataprovider.start_date, "%Y-%m-%d")
        start_date = min(
            start_date  - interval_to_timedelta[self.dataprovider.interval] * 50, 
            start_date - timedelta(days=1)
        )
        self.dataprovider.start_date = start_date.strftime("%Y-%m-%d")

    def apply_transform(self, data : pd.DataFrame):
        data = self.dataprovider.getData()
        data.ta.strategy("all")
        # returns data from the start_date
        return data[self.initial_start_date:]

class AEDataTransformer(DataTransformer):
    """Use auto-encoder to reduce dimensionality of data. If no model if found, a new model will be trained.
    """

    def __init__(
            self,
            dataprovider :
            DataProvider,
            modelstore : ModelStore,
            metamodelstore : MetaModelStore) -> None:
        """Create a new AEDataTransformer
        

        Args:
            dataprovider (DataProvider): Data source
            modelstore (ModelStore): Where to store or found the model
            metamodelstore (MetaModelStore): Where to store or found the metamodel
        """
        super().__init__(dataprovider)
        self.modelstore = modelstore
        self.metamodelstore = metamodelstore

    def concat_columns_list(self):
        pass

    def apply_transform(self, data : pd.DataFrame):
        pass
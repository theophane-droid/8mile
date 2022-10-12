from abc import abstractmethod

import pandas_ta as ta

from Hmile.DataProvider import DataProvider

class DataTransformer:
    """Abstraction class to apply data transformation
    """

    def __init__(self, dataprovider : DataProvider) -> None:
        self.dataprovider = dataprovider

    @abstractmethod
    def transform(self):
        """Apply transformation
        """
        raise NotImplementedError()


class TaFeaturesTransformer(DataTransformer):
    def __init__(self, dataprovider : DataProvider) -> None:
        """Apply all technical analysis features to the data

        Args:
            dataprovider (Hmile.DataProvider.Dataprovider): Dataprovider to transform
            ta_features (list): list of technical analysis features to apply
        """
        super().__init__(dataprovider)

    def transform(self):
        data = self.dataprovider.getData()
        data.ta.strategy("all")
        return data



# TODO:
# - tafeatures
# - encoder
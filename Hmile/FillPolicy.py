from abc import abstractmethod

import pandas as pd
from pandas.tseries.offsets import DateOffset

from Hmile.Exception import NoFillPolicySet

offset_by_interval = {
    'day' : DateOffset(days=1),
    'hour' : DateOffset(hours=1),
    'minute' : DateOffset(minutes=1),
}

class FillPolicy:
    """Abstract class for fill policy. A fill policy is used to fill missing dates in a dataframe. A fill policy is automatically called if needed
    """
    def __init__(self, interval):
        """Initialize the fill policy

        Args:
            interval (str): Interval of the dataframe. Can be 'day', 'hour' or 'minute'
        """
        self.interval = interval

    @abstractmethod
    def __call__(self, dataframe):
        """Fill the dataframe with missing dates

        Args:
            dataframe (pd.DataFrame): dataframe to fill
        """
        raise NotImplementedError()

class FillPolicyError(FillPolicy):
    """Fill policy that raise an exception if missing dates are found"""
    def __call__(self, dataframe):
        raise NoFillPolicySet("FillPolicyError: FillPolicy is not set")

class FillPolicyClip(FillPolicy):
    """Fill policy that juste ignore missing dates"""
    def __call__(self, dataframe):
        return dataframe

class FillPolicyAkima(FillPolicy):
    """Fill policy that use akima interpolation to fill missing dates"""
    def __call__(self, dataframe):
        ideal_date_range = pd.date_range(
            start=dataframe.index[0],
            end=dataframe.index[-1],
            freq=offset_by_interval[self.interval])
        return dataframe.interpolate(method='akima')
import unittest
import pandas as pd

from hmile.FillPolicy import FillPolicyAkima, FillPolicyClip, FillPolicyError


dataframe = pd.DataFrame(
    data={
        'open' : [1, 2, 3, 4, 5],
        'close' : [1, 2, 3, 4, 5],
        'high' : [1, 2, 3, 4, 5],
        'low' : [1, 2, 3, 4, 5],
    },
    index=pd.date_range(start='2020-01-01', periods=5, freq='D')
)
dataframe = dataframe.drop(dataframe.index[1])

class TestAkima(unittest.TestCase):
    def setUp(self):
        self.fillpolicy = FillPolicyAkima('day')
        self.dataframe = dataframe.copy()
    
    def test_normal(self):
        dataframe = self.fillpolicy.__call__(self.dataframe)
        self.assertEqual(len(dataframe), 5)
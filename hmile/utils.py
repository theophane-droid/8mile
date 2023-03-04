import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
from tqdm import tqdm
from hmile.ModelStore import ElasticModelStore
import warnings
warnings.filterwarnings("ignore")

def get_min_dict(pairs : dict) -> list:
    """return the min of a dict with severals pairs

    Args:
        pairs (dict): dict of pairs

    Returns:
        list : list of min
    """
    min = None
    for _,df in pairs.items() :
        if min is None :
            min = df.min().values
        else :
            min = np.minimum(min,df.min().values)

        if type(list(min)[0]) == list :
            raise("error min is not a single list")
        return list(min)

def get_max_dict(pairs : dict) -> list:
    """return the max of a dict with severals pairs

    Args:
        pairs (dict): dict of pairs

    Returns:
        list : list of max
    """
    max = None
    for _,df in pairs.items() :
        if max is None :
            max = df.max().values
        else :
            max = np.maximum(max,df.max().values)
    
        if type(list(max)[0]) == list :
            raise("error max is not a single list")
    return list(max)


def merge_columns(pairs : dict) :
    """ keep only common indicators between multiples pairs

    Args:
        pairs (dict): dict of pairs

    Returns:
        dict of actuated pairs 
    """
    init = True
    cols : pd.Index = None
    for _,df in pairs.items() :
        if init :
            cols = df.columns
            init = False
        else :
            cols = cols.intersection(df.columns)
    cols = cols.drop_duplicates(keep='first')
    to_keep = cols.values.tolist()
    for pair,df in pairs.items() :
        pairs[pair] = df[to_keep]
    return pairs

def get_number_lines(pairs : dict) :
    lines = []
    for _,df in pairs.items() :
        lines.append(df.shape[0])
    return lines

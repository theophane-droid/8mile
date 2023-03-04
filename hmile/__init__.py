import os

from .__version__ import __version__, __author__

from .DataProvider import YahooDataProvider as Yahooprovider
from .DataProvider import CSVDataProvider as Csvprovider
from .DataProvider import PolygonDataProvider as Polygonprovider
from .DataProvider import ElasticDataExporter as Elasticprovider
from .DataExporter import CSVDataExporter as Csvexporter
from .DataExporter import ElasticDataExporter as Elasticexporter
from .DataTransformer import TaDataTransformer as TATransformer

RABBIT_BANNER =  """
   ______         .__.__          
 /  __  \  _____ |__|  |   ____  
 >      < /     \|  |  | _/ __ \ 
/   --   \  Y Y  \  |  |_\  ___/ 
\______  /__|_|  /__|____/\____>
       \/      \/              
**v{} by {}**
""" .format(__version__, __author__)


if not 'HMILE_BANNER' in os.environ or os.environ['HMILE_BANNER'] != 'disable':
    print(RABBIT_BANNER)
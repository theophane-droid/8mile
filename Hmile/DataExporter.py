from typing import Union
from abc import abstractmethod

from elasticsearch import Elasticsearch, helpers

from Hmile.DataProvider import DataProvider
from Hmile.DataTransformer import DataTransformer

class DataExporter:
    """Export data to another format

    :ivar dataprovider: Source of the data to export    
    """
    def __init__(self,
        dataprovider : Union[DataProvider, DataTransformer]):
        """Initialize the DataExporter

        Args:
            dataprovider (Union[DataProvider, DataTransformer]): the source of the data to transform
        """
        self.dataprovider = dataprovider

    def export(self) -> None:
        """Apply export and store result

        Raises:
            TypeError: if dataprovider is not a DataProvider or a DataTransformer
        """
        if isinstance(self.dataprovider, DataProvider):
            data = self.dataprovider.getData()
            interval = self.dataprovider.interval
        elif isinstance(self.dataprovider, DataTransformer):
            data = self.dataprovider.transform()
            interval = self.dataprovider.dataprovider.interval
        else:
            raise TypeError('dataprovider must be a DataProvider or a DataTransformer')
        self.export_func(data, interval)
    
    @abstractmethod
    def export_func(self, data, interval):
        raise NotImplementedError()

class CSVDataExporter(DataExporter):
    """
    Export data to csv. The file name will be in the format {pair}-{interval}.csv
    
    :ivar dataprovider: Source of the data to export    
    :ivar directory: directory in with the csv will be saved
    """
    def __init__(self,
        dataprovider : Union[DataProvider, DataTransformer],
        directory : str):
        """Export data to csv. The file name will be in the format {pair}-{interval}.csv

        Args:
            dataprovider (Hmile.DataProvider.Dataprovider): Dataprovider to export
            directory (str): directory in with the csv will be saved
        """
        super().__init__(dataprovider)
        self.directory = directory

    def export_func(self, data, interval):
        for pair in data.keys():
            name = f'{self.directory}/f-{pair.lower()}-{interval}.csv'
            data[pair].to_csv(name, index=True)


class ElasticDataExporter(DataExporter):
    """Export data to ElasticSearch. The index name will be in the format f-{pair}-{interval

    :ivar dataprovider: Source of the data to export    
    :ivar es_url: ElasticSearch url
    :ivar es_user: ElasticSearch user
    :ivar es_pass: ElasticSearch password
    """
    def __init__(
        self,
        dataprovider: DataProvider,
        es_url: str,
        es_user: str,
        es_pass: str):
        super().__init__(dataprovider)
        self.es_url = es_url
        self.es_user = es_user
        self.es_pass = es_pass
    
    def export_func(self, data, interval):
        es = Elasticsearch(self.es_url, http_compress=True, verify_certs=False, http_auth=(self.es_user, self.es_pass))
        for pair in data.keys():
            index_name = f'f-{pair.lower()}-{interval}'
            helpers.bulk(es, ElasticDataExporter.doc_generator(data[pair], index_name))


    def doc_generator(df, index_name):
        df_iter = df.iterrows()
        for index, document in df_iter:
            data_dict = document.to_dict()
            data_dict['@timestamp'] = index
            data_result = {}
            for k in data_dict:
                # if does not begin with obv
                if not k.startswith('obv'):
                    key_name = k.lower().replace('.', '_')
                    value = data_dict[k]
                    data_result[key_name] = value

            yield {
                    "_index": index_name,
                    'doc_type':'_doc',
                    "_id" : data_result['@timestamp'],
                    "_source": data_result,
            }
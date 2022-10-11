from abc import abstractmethod

from elasticsearch import Elasticsearch, helpers

from Hmile.DataProvider import DataProvider

class DataExporter:
    """Export data to another format

    Args:
        DataProvider (Hmile.DataProvider.Dataprovider): Dataprovider to export
    """
    def __init__(self,
        dataprovider : DataProvider):
        self.dataprovider = dataprovider

    @abstractmethod
    def export(self):
        """Do export
        """
        raise NotImplementedError()

class CSVDataExporter(DataExporter):
    def __init__(self,
        dataprovider : DataProvider,
        directory : str):
        """Export data to csv. The file name will be in the format {pair}-{interval}.csv

        Args:
            dataprovider (Hmile.DataProvider.Dataprovider): Dataprovider to export
            directory (str): directory in with the csv will be saved
        """
        super().__init__(dataprovider)
        self.directory = directory

    def export(self):
        name = f'{self.directory}/f-{self.dataprovider.pair.lower()}-{self.dataprovider.interval}.csv'
        self.dataprovider.getData().to_csv(name, index=True)


class ElasticDataExporter(DataExporter):
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
    
    def export(self):
        index_name = f'f-{self.dataprovider.pair.lower()}-{self.dataprovider.interval}'
        es = Elasticsearch(self.es_url, http_compress=True, verify_certs=False, http_auth=(self.es_user, self.es_pass))
        data = self.dataprovider.getData()
        helpers.bulk(es, ElasticDataExporter.doc_generator(data, index_name))


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
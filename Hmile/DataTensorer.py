from abc import ABC, abstractmethod
from textwrap import fill
from Hmile.DataProvider import DataProvider,ElasticDataProvider, CSVDataProvider, PolygonDataProvider, YahooDataProvider
from Hmile.FillPolicy import FillPolicyAkima, FillPolicyClip, FillPolicyError
from Hmile.DataTransformer import TaDataTransformer
from Hmile.utils import AE,apply_encoder, request_elastic_model, get_min_dict,get_max_dict
import torch


FillPolicy = {
    "akima" : FillPolicyAkima,
    "clip" : FillPolicyClip,
    "default" : FillPolicyError
}

Provider = {
    "elastic" : ElasticDataProvider,
    "csv" : CSVDataProvider,
    "yahoo" : YahooDataProvider,
    "polygon" : PolygonDataProvider
}

class Tensorer(ABC) :
    """
    Base class for simulation environnement and maket place simulation

    Methods :
     - get_{min/max}_indices to set up the min max of the observation space
     - reset to reset all env (called at the beginning)
     - reset_by_id to select environnement to reset

     - get_indicators (iterate over the time to send current indicators and increment the time)

    """
    @abstractmethod
    def reset_by_id(self,indices : torch.Tensor) :
        """
        reset specified environnement. Called each step by the simulation

        Args:
            indices (torch.Tensor): tensor that indicate which envs need to be reseted
        """
        pass
    
    @abstractmethod
    def reset(self):
        """
        reset all the environnement (used as init most of the time)
        """
        pass

    @abstractmethod     
    def get_indicators(self):
        """get new indicators : called each step to actuate observations
        """
        pass

    @abstractmethod
    def get_min_indices(self) -> list :
        """
        return min of each component from the observation space. Usefull for defining the min/max of obs space

        Returns:
            list: list of min
        """
        pass

    @abstractmethod
    def get_max_indices(self) -> list :
        """
        return max of each component from the observation space. Usefull for defining the min/max of obs space

        Returns:
            list: list of max
        """
        pass


class SingleFeaturesDataTensorer(Tensorer):
    """
    create usable training environnement for RL training,


    """
    def __init__(self,
        episode_max_length : int,
        provider_type : str,
        provider_configuration : dict,
        nb_env : int,
        device : str = None,
        pairs : list = ["BTCUSD"],
        start_date : str = "2021-02-24",
        end_date : str = "2022-06-04",
        fill_policy : str = "default",
        interval : str = "hour",
        encoder_configuration : dict = None
        ) -> None:
        """create the simulation environement for trading

        To make it easier and readable, You can only pass the episode_length and the environment part of the cfg as arguments

        Args:
            episode_max_length (int) : max length of an episode
            provider_type (str) : type of the provider (elastic/csv/yahoo)
            provider_configuration (dict): dataprovider parameters (see 8mile documentation to see what is needed)
            nb_env (int): number of parallele environments
            device (str, optional): cuda or cpu. Defaults to "cpu".
            pair (list, optional): list of pairs to use . Defaults to ["BTCUSD"].
            start_date (str, optional): start date of dataset. Defaults to "2021-02-24".
            end_date (str, optional): end date of dataset. Defaults to "2022-06-04".
            fill_policy (str, optionnal) : method to fill missing values (akimia/clip/error). see 8mile doc. Defaults to error
            interval (str, optional): interval between each time step. Defaults to "hour".
            encoder_configuration (dict, optinal) : usefull if encoder stored in an Elastic DB and a config file, use it automatically
        """
        provider_configuration["pairs"] = pairs
        provider_configuration["start_date"] = start_date
        provider_configuration["end_date"] = end_date
        provider_configuration["interval"] = interval

        provider : DataProvider = Provider[provider_type](**provider_configuration)
        provider.fill_policy = FillPolicy[fill_policy](interval)

        transformer = TaDataTransformer(provider)
        self.data = transformer.transform()

        self.nb_pairs = len(self.data)
        self.pairs = list(self.data.keys())
        self.shape = self.data[self.pairs[0]].shape
        self.nb_env = nb_env
        if device != None :
            self.device = device
        else :
            if torch.cuda.is_available() :
                self.device = "cuda"
            else :
                self.device = "cpu"
        if self.device == "cuda" :
            if not torch.cuda.is_available() :
                self.device = "cpu"
        
        self.episode_max_length = episode_max_length
        self.create_tensors()

        if encoder_configuration != None :
            AE = request_elastic_model(**encoder_configuration)
            self.apply_encoder(AE)

        
    def create_tensors(self):
        self.current_step = torch.zeros(self.nb_env,2,device=self.device,dtype=torch.long)
        self.indicators = torch.zeros(self.nb_pairs,*self.shape,device=self.device,dtype=torch.float64)
        self.ohlcv = torch.zeros(self.nb_pairs,self.shape[0],5,device=self.device,dtype=torch.float64) #open high low close volume for each pair
        for i,(_,df) in enumerate(self.data.items()):
            ohlcv = df[["open","high","low","close","volume"]]
            self.ohlcv[i] = torch.tensor(ohlcv.values,device=self.device,dtype=torch.float64)
            self.indicators[i] = torch.tensor(df.values,device= self.device,dtype=torch.float64)
        self.min = get_min_dict(self.data)
        self.max = get_max_dict(self.data)
        self.max_gains = torch.zeros(self.nb_env,device=self.device,dtype=torch.float64)
    
    def apply_encoder(self, encoder : AE) :
        """
        apply if possible the encoder given to the indicators

        Args:
            encoder (AE): see doc
        """
        data = apply_encoder(encoder,self.data)
        self.shape = data[self.pairs[0]].shape
        self.indicators = torch.zeros(self.nb_pairs,*self.shape,device=self.device,dtype=torch.float64)
        for i,(_,tens) in enumerate(data.items()):
            self.indicators[i] = tens.to(self.device)
        if encoder.normalize_output :
            self.min = [-1]*self.shape[1]
            self.max = [1]*self.shape[1]
        #TODO : implement else


    def apply_rolling_normalization(self, data : torch.Tensor):


        mean = torch.clone(data) # moyenne glissante
        var = torch.clone(data) # variance glissante

        for i in range (data.size()[0]):
            if i < self.mean_window_size:
                mean[i] = torch.mean(data[0:self.mean_window_size], dim=0)
                var[i] = torch.var(data[0:self.mean_window_size], dim=0)
            else:
                mean[i] = torch.mean(data[i-self.mean_window_size:i], dim=0)
                var[i] = torch.var(data[i-self.mean_window_size:i], dim=0)

        diff = torch.sub(data, mean)
        out = torch.div(diff, torch.sqrt(var))
        return out

    

    def reset_by_id(self,indices : torch.Tensor) :
        """

        Args:
            indices (torch.Tensor): tensor of 1 and 0 to specifie which envs need to be reseted
        
        Return : 
            True if nothing to reset
        """
        if indices.shape[0] == 0 :
            return True
        begin_indices = torch.randint(0,self.shape[0]-self.episode_max_length,(indices.shape[0],),device=self.device,dtype=torch.long)
        pair = torch.randint(0,self.nb_pairs,(indices.shape[0],),device=self.device,dtype=torch.long)
        self.current_step[indices,0] = pair
        self.current_step[indices,1] = begin_indices
        for i in indices.detach().cpu().numpy() :
            env = self.ohlcv[self.current_step[i,0],self.current_step[i,1]:self.current_step[i,1]+self.episode_max_length,0:-1]
            self.max_gains[i] = torch.max(env)/torch.min(env)


    def reset(self):
        self.reset_by_id(torch.range(0,self.nb_env-1,device=self.device,dtype=torch.long))
                
    def get_indicators(self):
        """return indicators and ohlcv for each env at each timestep

        Returns:
            tuple(torch.tensor, torch.tensor) : (indicators, ohlcv)
        """
        indicators = self.indicators[self.current_step[:,0],self.current_step[:,1]]
        ohlcv = self.ohlcv[self.current_step[:,0],self.current_step[:,1]]
        self.current_step[:,1] += 1
        # return indicators from self.mean_window_size to end
        #TODO : end that (need to be tested)
        return indicators, ohlcv
    def max_range(self) -> torch.Tensor :
        return self.max_gains

    def get_min_indices(self) -> list :
        return self.min 

    def get_max_indices(self) -> list :
        return self.max

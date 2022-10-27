from abc import ABC, abstractmethod
from textwrap import fill
from Hmile.DataProvider import DataProvider,ElasticDataProvider, CSVDataProvider, PolygonDataProvider, YahooDataProvider
from Hmile.FillPolicy import FillPolicyAkima, FillPolicyClip, FillPolicyError
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
        episode_length : int,
        provider_type : str,
        provider_configuration : dict,
        nb_env : int,
        device : str = "cpu",
        pairs : list = ["BTCUSD"],
        start_date : str = "2021-02-24",
        end_date : str = "2022-06-04",
        fill_policy : str = "default",
        interval : str = "hour",
        
        ) -> None:
        """create the simulation environement for trading

        To make it easier and readable, You can only pass the episode_length and the environment part of the cfg as arguments

        Args:
            episode_length (int) : max length of an episode
            provider_type (str) : type of the provider (elastic/csv/yahoo)
            provider_configuration (dict): dataprovider parameters (see 8mile documentation to see what is needed)
            nb_env (int): number of parallele environments
            device (str, optional): cuda or cpu. Defaults to "cpu".
            pair (list, optional): list of pairs to use . Defaults to ["BTCUSD"].
            start_date (str, optional): start date of dataset. Defaults to "2021-02-24".
            end_date (str, optional): end date of dataset. Defaults to "2022-06-04".
            fill_policy (str, optionnal) : method to fill missing values (akimia/clip/error). see 8mile doc. Defaults to error
            interval (str, optional): interval between each time step. Defaults to "hour".
        """
        provider_configuration["pairs"] = pairs
        provider_configuration["start_date"] = start_date
        provider_configuration["end_date"] = end_date
        provider_configuration["interval"] = interval

        provider : DataProvider = Provider[provider_type](**provider_configuration)
        provider.fill_policy = FillPolicy[fill_policy](interval)
        self.data = provider.getData()
        self.size = self.data.shape[0]
        self.nb_env = nb_env
        self.device = device
        self.episode_length = episode_length
        self.create_tensor()
        
    def create_tensor(self):
        self.current_step = torch.zeros(self.nb_env,device=self.device,dtype=torch.long)
        self.provider = torch.zeros(self.nb_env,device=self.device,dtype=torch.float64)
        self.reset()
    
    def normalize(self, data):

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
        return torch.clip(out, min=MIN, max=MAX)

    

    def reset_by_id(self,indices : torch.Tensor) :
        """

        Args:
            indices (torch.Tensor): tensor of 1 and 0 to specifie which envs need to be reseted
        
        Return : 
            True if nothing to reset
        """
        if indices.shape[0] == 0 :
            return True
        begin_indices = torch.randint(0,self.size-self.episode_length,(indices.shape[0],),device=self.device,dtype=torch.long)
        self.current_step[indices] = begin_indices

    def reset(self):
        self.reset_by_id(torch.ones(self.nb_env,device=self.device,dtype=torch.bool))
                
    def get_indicators(self):
        norm_indicators = DataTensorer.norm_data[self.current_step]
        indicators = DataTensorer.data[self.current_step]
        self.current_step+=1
        # return indicators from self.mean_window_size to end
        return norm_indicators, indicators

    def get_min_indices(self) -> list :
        return [-10 for _ in range(DataTensorer.size)] 

    def get_max_indices(self) -> list :
        return [10 for _ in range(DataTensorer.size)]

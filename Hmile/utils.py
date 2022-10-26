import torch
from torch import nn
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from Hmile.DataProvider import DataProvider
import warnings
warnings.filterwarnings("ignore")

null = None

class DataTensorer:
    """Can be used to transform data into pytorch tensor
    """
    data = null
    norm_data = null
    min = null
    max = null
    size = null
    MIN = -10
    MAX = 10
    def __init__(
        self,
        dataprovider : DataProvider,
        nb_env,
        nb_data_per_session,
        device,
        mean_window_size=300,
        window_size=-1
        ) -> None:
        """Initialize the DataTensorer

        Args:
            dataprovider (DataProvider): Dataprovider to use to get the data
            nb_env (int): size of dim 3 of the tensor
            nb_data_per_session (str): size of dim 2 of the tensor
            device (str): pytorch device to use
            mean_window_size (int, optional): Window for rolling mean normalization. Defaults to 300.
            window_size (int, optional): size of dim 1. Defaults to -1.
        """        

        self.window_size = window_size
        self.mean_window_size = mean_window_size
        if DataTensorer.data == null :
            df = dataprovider.getData()
            df.fillna(method="ffill",inplace=True)
            df.fillna(method="bfill",inplace=True)
            DataTensorer.size = df.shape[1]
            DataTensorer.data = torch.tensor(df.to_numpy(), device=device)
            DataTensorer.norm_data = self.normalize(DataTensorer.data)
        
        self.size = DataTensorer.norm_data.shape[0]
        self.nb_env = nb_env
        self.nb_data_per_session = nb_data_per_session
        self.device = device
        self.create_tensor()
        

    def normalize(self, data):
        """Apply rolling mean and variance normalization. 
        The result is clipped between -10 and 10 
        
        Args:
            data (torch.tensor): tensor to normalize
        """

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
        return torch.clip(out, min=DataTensorer.MIN, max=DataTensorer.MAX)

    def create_tensor(self):
        self.current_step = torch.zeros(self.nb_env,device=self.device,dtype=torch.long)
        self.provider = torch.zeros(self.nb_env,device=self.device,dtype=torch.float64)
        self.reset()

    def reset_by_id(self,indices) :
        """Reset the current step for the given indices

        Args:
            indices (list): list of indices to reset
        """
        if indices.shape[0] == 0 :
            return True
        begin_indices = torch.randint(self.mean_window_size,self.size-self.nb_data_per_session-5,(indices.shape[0],),device=self.device,dtype=torch.long)
        self.current_step[indices] = begin_indices

    def reset(self):
        """Reset the current step for all indices
        """
        self.reset_by_id(torch.ones(self.nb_env,device=self.device,dtype=torch.bool))
                
    def get_indicators(self):
        """Returns normalized and unnormalized data
        
        Returns:
            tuple: (unnormalized data : torch.Tensor, normalized data : torch.Tensor)"""

        norm_indicators = DataTensorer.norm_data[self.current_step]
        indicators = DataTensorer.data[self.current_step]
        self.current_step+=1
        return norm_indicators, indicators

    def get_min_indices(self) -> list :
        """Returns the min for each feature

        Returns:
            list: result
        """
        return [-10 for _ in range(DataTensorer.size)] 

    def get_max_indices(self) -> list :
        """Returns the max for each feature

         Returns:
            list: result
        """
        return [10 for _ in range(DataTensorer.size)]

def getActivateFunction(i : int ,index : int,normalize : bool) :
    if i == index-1 and normalize:
        return nn.Tanh()
    return nn.PReLU()
    


class AE(nn.Module):
    """ Create an Autoencoder. this autoencoder contains severals interesting attributes :

    - the encoder (can be used alone by self.encoder.forward(...))
    - the decoder (can be used alone by self.decoder.forward(...))
    - the norm of the data used (for normalization) with self.norm (gives dict with mean/std for each pairs)
    - the name of the columns of the dataset with self.column_names
    """
    def __init__(self, norm : dict,column_names : list,input_shape : int, nb_neurones : list, normalize_output : bool = False):
        """
        Create Autoencoder depending on different parameters

        Args:
            norm (dict): dict of each mean and std for each paur
            column_names (list): column_namethe final dataset
            input_shape (int): input length
            nb_neurones (list): list of layers with their number of neurones for the whole AE.
            normalize_output (bool, optional): if true, output features of encoder will be btw [-1,1]. Defaults to False.
        """
        super().__init__()
        self.norm = norm
        self.column_names = column_names
        nn_values = nb_neurones
        nn_values.append(input_shape)
        nn_values.insert(0,input_shape)
        index = nn_values.index(np.min(nn_values))
        self.encoder= nn.Sequential(*flatten([[nn.Linear(nn_values[i],nn_values[i+1]),getActivateFunction(i,index,normalize_output)] for i in range(index)]))
        self.decoder = nn.Sequential(*flatten([[nn.Linear(nn_values[i],nn_values[i+1]),nn.PReLU()] for i in range(index,len(nn_values)-1)]))
        #self.last_layer = nn.Sequential(nn.Linear(nn_values[-2],nn_values[-1]),nn.PReLU())
        
        print("#################  Encoder ###############\n")
        print(self.encoder)
        print()
        print("#################  Decoder ###############\n")
        print(self.decoder)
        print()


    def forward(self, features):
        encoded = self.encoder(features)
        reconstructed = self.decoder(encoded)
        return reconstructed

def print_precision(initial_data : np.array, predicted_data : np.array) :
    diff = np.abs(initial_data - predicted_data)
    print("la moyenne des erreurs est {}".format(np.mean(np.mean(diff,axis=0))))

def flatten(list) :
    new = []
    for i in list :
        new += i
    return new


def concatAndNormDf(dict : dict, normalize : bool= True) -> tuple :
    """from a df dictionnary, return a single df in which all df are concatenated/normalized by pairs and return the mean and std of those df aswell in a dictionnary
     !!!!    keep only columns that are available for all pairs   !!!!
    Args:
        dict (dict): dict of all df by pairs
        normalize (boolean) : normalize all the dataset if set to true. Defaults True
    Return:

        (pd.Dataframe, dict ): concatenated df from all pairs and dict of mean/std
    """
    init = True
    finaldf = pd.DataFrame()
    norm = {}
    for pair, df in dict.items() :
        mean = df.mean()
        std = df.std()
        inter = (df-mean)/std if normalize else df
        if init : 
            finaldf = inter
            init = False
        else :
            finaldf = pd.concat([finaldf,inter], ignore_index = True)
        norm[pair] = { "mean" : mean, "std" : std}
    finaldf.dropna(axis=1,inplace=True)
    cols_to_keep = finaldf.columns
    for pair, dict in norm.items() :
        dict["mean"] = dict["mean"][cols_to_keep]
        dict["std"] = dict["std"][cols_to_keep]
        norm[pair] = dict
    return finaldf, norm


def trainAE(pairs : dict, 
            nb_out_components : int = 60, 
            is_normalized : bool = False,
            display : bool = True,
            test_percent : float = 0.1, 
            architecture : list = [200,150,100],
            normalize_output : bool = False,
            nb_epoch : int = 200, 
            lr : float = 1e-4,
            batch_size : int = 128,
            test_batch_size : int = 32) -> AE :
    """function to train an autoencoder

    Args:
        pairs (dict): dict of pairs dataframe on which the autoencoder will be trained.
        nb_out_components (int, optional): final number of features. Defaults to 40.
        is_normalized (bool, optional): specify if dataset is already normalized or need to be. Defaults to False.
        display (bool, optional): display results of the training. Defaults to True.
        test_percent (float, optional): part of the dataset kept for test. Defaults to 0.1.
        architecture (list, optional): architecture of the encoder (decoder is the symetric). Defaults to [200,150,100].
        nb_epoch (int, optional): nb epoch for learning. Defaults to 200.
        lr (float, optional): learning rate. Defaults to 1e-4.
        batch_size (int, optional): batch size of train dataset. Defaults to 128.
        test_batch_size (int, optional): batch size of test dataset. Defaults to 32.

    Returns:
        autoencoder : return the full autoencoder with mean and std of the dataset used and name of the columns
    """
    ## normalization ##
    df, norm = concatAndNormDf(pairs, normalize= not is_normalized)
    ## architecture configuration ###
    if df.isnull().values.any() :
        raise("error can't treat dataset with NaNs, please fix that !")
    decoder = architecture[:]
    decoder.reverse()
    architecture.append(nb_out_components)
    archi = architecture + decoder


    #### pytorch model creation ####
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if display :
        print("device is {}".format(device))
    model = AE(input_shape=df.shape[1],nb_neurones = archi, norm = norm,column_names=df.columns,normalize_output=normalize_output).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()


    #### dataset creation ####
   
    train_dataset,test_dataset = train_test_split(df,test_size=test_percent,shuffle=True)
    train_loader = torch.utils.data.DataLoader(
        train_dataset.values, batch_size=batch_size, shuffle=True, num_workers=4, pin_memory=True
    )
    test_loader = torch.utils.data.DataLoader(
        test_dataset.values, batch_size=test_batch_size, shuffle=False, num_workers=4
    )


    ### model train and test ###
    l_loss = []
    pbar = tqdm(range(nb_epoch))
    for _ in pbar:
        loss = 0
        for batch_features in train_loader:
            batch_features = batch_features.float().to(device)
            optimizer.zero_grad()
            outputs = model(batch_features)
            train_loss = criterion(outputs, batch_features)
            train_loss.backward()
            optimizer.step()
            loss += train_loss.item()
        loss = loss / len(train_loader)
        l_loss.append(loss)
        pbar.set_description("Processing loss : %s" % str(round(loss,4)))
        
    ##test phase
    test_loss = 0
    for _ in test_loader :
        batch_features = batch_features.float().to(device)
        outputs = model(batch_features)
        i_loss = criterion(outputs, batch_features)
        test_loss += i_loss.item()
        if display :
            print("test_loss : ", round(test_loss/len(test_loader), 4))    
    if display :
        Y = model(torch.Tensor(df.values))
        print_precision(df.values,Y.cpu().detach().numpy())
        plt.plot(l_loss)
        plt.grid()
        plt.title("evolution courbe de loss")
        plt.show()

    return model
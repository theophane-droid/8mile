import torch
from torch import nn
import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from Hmile.ModelStore import ElasticModelStore
import warnings
warnings.filterwarnings("ignore")

def flatten(list) :
    new = []
    for i in list :
        new += i
    return new

def get_min_dict(pairs : dict) -> list:
    min = None
    for _,df in pairs :
        if min is None :
            min = df.min().values
        else :
            min = np.minimum(min,df.min().values)

        if type(list(min)[0]) == list :
            raise("error min is not a single list")
        return list(min)

def get_max_dict(pairs : dict) :
    max = None
    for _,df in pairs :
        if max is None :
            max = df.max().values
        else :
            max = np.maximum(max,df.max().values)
    
        if type(list(max)[0]) == list :
            raise("error max is not a single list")
    return list(max)



def getActivateFunction(i : int ,index : int,normalize : bool) :
    if i == index-1 and normalize:
        return nn.Tanh()
    return nn.PReLU()

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

class AE(nn.Module):
    """ Create an Autoencoder. this autoencoder contains severals interesting attributes :

    - the encoder (can be used alone by self.encoder(...))
    - the decoder (can be used alone by self.encoder(...))
    - the norm of the data used (for normalization) with self.norm (gives dict with mean/std for each pairs)
    - the name of the columns of the dataset with self.column_names
    """
    def __init__(self, norm : dict,column_names : list,input_shape : int, nb_neurones : list, normalize_output : bool = False):
        """
        Create Autoencoder depending on different parameters

        Args:
            norm (dict): dict of each mean and std for each pair
            column_names (list): column_namethe final dataset
            input_shape (int): input length
            nb_neurones (list): list of layers with their number of neurones for the whole AE.
            normalize_output (bool, optional): if true, output features of encoder will be btw [-1,1]. Defaults to False.
        """
        super().__init__()
        self.norm = norm
        self.column_names = column_names
        self.normalize_output = normalize_output
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


def request_elastic_model(es_url : str, es_user : str, es_pass : str, searching_args : dict) -> AE :
    """seach in an es DB model and return it

    Args:
        es_url (str): url de la BDD elastic
        es_user (str): user pour la bdd
        es_pass (str): password for the user
        searching args (dict): tags, description.... look at hmile doc for more information

    Returns:
        AE: autoencoder
    """
    # we create a MetaModelStore object
    meta_model_store = ElasticModelStore(
        es_url,
        es_user,
        es_pass)

    # we retrieve the list of models with the tag 'test'
    meta_model_list = meta_model_store.get(**searching_args)

    # we now get the model
    model = meta_model_list[-1].model
    if model is not None :
        return model

def print_precision(initial_data : np.array, predicted_data : np.array) :
    diff = np.abs(initial_data - predicted_data)
    prec = np.mean(np.mean(diff,axis=0))
    print("la moyenne des erreurs est {}".format(prec))
    return prec




def apply_encoder(encoder : AE, pairs : dict) -> dict :
    """apply the encoder part of an Autoencoder to a list of pairs

    warning : the AE need to be trained with these pairs to be used with them. 
    
    Please do not normalize the indicators since it will be done with the values known by the AE for each pairs

    Args:
        encoder (AE): Autoencoder model to use for this transformation
        pairs (dict): pairs to transforme

    Returns:
        dict: indicators returned
    """
    encoder.training = False

    for pair,df in pairs.items() :
        if not all(col in encoder.column_names for col in list(df.columns)) :
            raise("error, indicators needed for autoencoder are not present in the dataset")
        if not pair in encoder.norm :
            raise("Autoencoder not trained with this pair")
        df = (df - encoder.norm[pair]["mean"])/encoder.norm[pair]["std"]
        df = df[encoder.column_names]
        pairs[pair] = encoder.encoder(df)
    return pairs


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
        precision : return precision of the model
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
    for batch_features in test_loader :
        batch_features = batch_features.float().to(device)
        outputs = model(batch_features)
        i_loss = criterion(outputs, batch_features)
        test_loss += i_loss.item()
    if display :
        print("test_loss : ", round(test_loss/len(test_loader), 4))    
    if display :
        Y = model(torch.Tensor(df.values))
        precision = print_precision(df.values,Y.cpu().detach().numpy())
        plt.plot(l_loss)
        plt.grid()
        plt.title("evolution courbe de loss")
        plt.show()

    return model, precision
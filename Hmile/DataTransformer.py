# TODO:
# - datatensorer
# - tafeatures
# - encoder

class DataTensorer:
    data = null
    norm_data = null
    min = null
    max = null
    size = null
    def __init__(
        self,
        dataprovider : DataProvider,
        nb_env,
        nb_data_per_session,
        device,
        mean_window_size=300,
        window_size=-1
        ) -> None:
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

    def create_tensor(self):
        self.current_step = torch.zeros(self.nb_env,device=self.device,dtype=torch.long)
        self.provider = torch.zeros(self.nb_env,device=self.device,dtype=torch.float64)
        self.reset()

    def reset_by_id(self,indices) :
        if indices.shape[0] == 0 :
            return True
        begin_indices = torch.randint(self.mean_window_size,self.size-self.nb_data_per_session-5,(indices.shape[0],),device=self.device,dtype=torch.long)
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
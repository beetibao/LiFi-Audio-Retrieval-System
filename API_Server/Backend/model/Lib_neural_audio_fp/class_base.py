import numpy as np
from tqdm import tqdm
from .eval.utils.get_index_faiss import get_index

class Model:
    def __init__(self, fp,pre):
        self.fp = fp
        self.pre=pre
    def __call__(self,x):
        return self.fp(self.pre(x))
    
class Search_Engine:
    def __init__(self,database, info_df,music_info,load_just_SO=False, index_type='ivfpq', nogpu=True, max_train=1e7):
        if load_just_SO==False:
            self.index = get_index(index_type, database, database.shape, (not nogpu), max_train)
            self.index.add(database)
            print(f'{len(database)} items from reference DB')
        else:
            self.index=database
        self.info_df = info_df
        self.music_info=music_info
    
    def search_info_music(self,name):
        # print(self.music_info)
        info = self.music_info[self.music_info["song_name"]==name]
        return {"singer_name":info.singer.values[0],
                "singer_YT_channel":info.link_singer.values[0],
                "song_YT_channel":info.link_playlist.values[0]}
    
    def search(self,query,k,just_best_item=True):
        # print("Check load change 2")
        D,I = self.index.search(x=query,k=k)
        # print(f"I shape: {I.shape}")
        n = query.shape[0]*query.shape[1]
        songs = {}
        songs_count = {}
        for i in tqdm(range(I.shape[0])):
            for index,name in enumerate(self.info_df.iloc[I[i]]["name"].values):
                # songs[name] = min(songs.get(name,float("INF")),D[i][index])
                songs[name] = songs.get(name,0)+1/(D[i][index]*np.sqrt(index+1))
                songs_count[name] = songs_count.get(name,0)+1/n
                
        p = np.array(list(songs.values()))
        count = np.array(list(songs_count.values()))
        product = p*count
        c = np.exp(product - np.max(product))
        d1 = c/c.sum()
        k = {name:(d1[index]) for index,name in enumerate(list(songs.keys())) if d1[index] >0}
        songs = sorted(k.items(), key=lambda item: item[1], reverse = True)
        
        if not just_best_item: return songs
        return songs[0][0]
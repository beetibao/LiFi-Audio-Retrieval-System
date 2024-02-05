import os
class User_Manager:
    def __init__(self,num_survive):
        self.num_survive = num_survive
        self.users_request = {}
        self.users = []
        self.session_woring= []
    
    def check_rules(self,user_id):
        if len(self.users) > self.num_survive:
            n_del = len(self.users) - self.num_survive
            user_not_active = set(self.users) - set(self.session_woring)
            if len(user_not_active)>0:
                user_not_active.remove(user_id)
                user_not_active = list(user_not_active)
                new_survivors = user_not_active[n_del:]
                for i in user_not_active[:n_del]:
                    if self.users_request[i]["queue_data"]!={}: 
                        new_survivors.append(i)
                        continue
                    self.users_request.pop(i)
                self.users = new_survivors+self.session_woring
    
    def __create_session(self):
        return dict(queue_data = [], status = "free")
    
    def create_new_user_session(self,user_id):
        self.check_rules(user_id)
        self.users_request.update({user_id:self.__create_session()})
        self.users.append(user_id)

    def set_status_user_session(self,user_id,status):
        self.users_request[user_id]["status"] = status
        self.check_rules(user_id)
        
    def write_data(self,user_id,status,data):
        self.check_rules(user_id)
        self.users_request[user_id]["status"] = status
        self.users_request[user_id]["queue_data"].append(data)

    def get_data(self,user_id):
        self.check_rules(user_id)
        data = self.users_request[user_id]["queue_data"]
        if len(data)>0:
            data=data.pop(0)
        else:
            data = ""
        return {
            "status_model": self.users_request[user_id]["status"],
            "data_model": data}
    
def process_name_song(song_name,search_music_info):
    print(f"song_name: {song_name}")
    song_name = song_name.strip("wav")[:-1]
    song_info=search_music_info(song_name)
    singer_name = song_info.pop("singer_name").strip().replace("_"," ")
    return dict(song_name=song_name.replace("_"," "),
                singer_name = singer_name,
                **song_info)

def model_predict(key,audio_file_path,nItems,predict_func,Manager,search_music_info):
    print(f"Call to predict: {audio_file_path}")
    try:
        print("Start_predict")
        t = predict_func(audio_file_path)
        print(t)
        os.remove(audio_file_path)
        d = {f"top{i+1}":process_name_song(t[i][0],search_music_info) for i in range(min(nItems,len(t)))}
        Manager.write_data(key,"success",d)
    except Exception as e:
        Manager.write_data(key,"error",{"error":str(e)})
        print(f"Error: {e}")
        return "An error occurred"
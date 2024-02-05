# import wave, os
# from pydub import AudioSegment
# # from model import predict
# # import model

# from multiprocessing import Process
# import multiprocessing as mp
# import threading

# from flask_cors import CORS
# from flask import Flask, render_template, request, redirect, url_for, jsonify

# app = Flask(__name__)
# cors = CORS(app)

# class User_Manager:
#     def __init__(self,num_survive):
#         self.num_survive = num_survive
#         self.users_request = {}
#         self.users = []
#         self.session_woring= []
    
#     def check_rules(self,user_id):
#         if len(self.users) > self.num_survive:
#             n_del = len(self.users) - self.num_survive
#             user_not_active = set(self.users) - set(self.session_woring)
#             if len(user_not_active)>0:
#                 user_not_active.remove(user_id)
#                 user_not_active = list(user_not_active)
#                 new_survivors = user_not_active[n_del:]
#                 for i in user_not_active[:n_del]:
#                     if self.users_request[i]["queue_data"]!={}: 
#                         new_survivors.append(i)
#                         continue
#                     self.users_request.pop(i)
#                 self.users = new_survivors+self.session_woring
    
#     def __create_session(self):
#         return dict(queue_data = [], status = "free")
    
#     def create_new_user_session(self,user_id):
#         self.check_rules(user_id)
#         self.users_request.update({user_id:self.__create_session()})
#         self.users.append(user_id)

#     def set_status_user_session(self,user_id,status):
#         self.users_request[user_id]["status"] = status
#         self.check_rules(user_id)
        
#     def write_data(self,user_id,status,data):
#         self.check_rules(user_id)
#         self.users_request[user_id]["status"] = status
#         self.users_request[user_id]["queue_data"].append(data)

#     def get_data(self,user_id):
#         self.check_rules(user_id)
#         data = self.users_request[user_id]["queue_data"]
#         if len(data)>0:
#             data=data.pop(0)
#         else:
#             data = ""
#         return {
#             "status": self.users_request[user_id]["status"],
#             "data": data
#         }

# Manager = User_Manager(5)
# thread_control = []
# mp.Value('AI_Audio_Model', model.__model)

# def process_name_song(song_name):
#     print(f"song_name: {song_name}")
#     return song_name.split(".")[0].replace("_"," ")

# def model_predict(key,audio_file_path,nItems):
#     print(f"Call to predict: {audio_file_path}")
#     try:
#         t = predict(audio_file_path)
#         # print(t)
#         os.remove(audio_file_path)
#         d = {f"top{i+1}":process_name_song(t[i][0]) for i in range(min(nItems,len(t)))}
            
#         # print("D: ",d)
#         Manager.write_data(key,"success",d)
#     except Exception as e:
#         Manager.write_data(key,"error",{"error":str(e)})
#         print(f"Error: {e}")
#         return "An error occurred"

# @app.route('/get-predict/<string:user_id>', methods=["GET"])
# def get_data_response(user_id):
#     return jsonify(Manager.get_data(user_id))

# @app.route('/send-query', methods=['POST'])
# def process_audio():
#     global status
#     try:
#         print("Has get request")

#         audio_data = request.files["audio"]
#         key = request.form['key']
#         nItems = int(request.form['nItems'])

#         Manager.create_new_user_session(key)

#         print(f"audio_data: {audio_data}")
#         print(f"key: {key}")
#         output_file = f"./audio_queries/{key}_recording.wav"
        
#         audio_data.save(output_file)
#         file = wave.open(output_file)
#         framerate = file.getframerate()
#         print(f"len: {file.getnframes()}")
#         print(f"framerate: {framerate}")
#         file.close()
#         if framerate!=8000:
#             audio = AudioSegment.from_wav(output_file)
#             resampled_audio = audio.set_frame_rate(8000)
#             resampled_audio.export(output_file, format='wav')
#             file = wave.open(output_file)
#             framerate = file.getframerate()
#             print(f"After resample len: {file.getnframes()}")
#             print(f"After resample framerate: {framerate}")
#             if file.getnframes()<8000*2:
#                 Manager.write_data(key,"error",{"error":"Music should be longer than 2 seconds"})
#                 os.remove(output_file)
#                 return "Music should be longer than 2 seconds"
#             file.close()
        
#         Manager.set_status_user_session(key,"working")
#         new_thread = threading.Thread(target=model_predict, args=(key,output_file,nItems))
#         thread_control.append(new_thread)
#         new_thread.start()
#         return "Successfully"
#     except Exception as e:
#         Manager.write_data(key,"error",{"error":str(e)})
#         print(f"Error: {e}")
#         return "An error occurred"
    
# @app.route('/')
# def main():
#     return "<h1>This is API Server</h1><p>Hello, World!</p>"

# if __name__ == "__main__":
#     #app.run(debug=True,host="127.0.0.5")
#     app.run()
import wave, os
from pydub import AudioSegment
from .model import predict,search_music_info
import threading

from flask import request, jsonify,Blueprint
from .utils import *

main = Blueprint('main', __name__)
Manager = User_Manager(5)
thread_control = []

@main.route('/get-predict/<string:user_id>', methods=["GET"])
def get_data_response(user_id):
    output = Manager.get_data(user_id)
    print(f"output = {output}")
    output = jsonify(output)
    print(f"output_jsonify = {output}")
    return output

@main.route('/send-query', methods=['POST'])
def process_audio():
    global status
    try:
        print("Has get request")

        audio_data = request.files["audio"]
        key = request.form['key']
        nItems = int(request.form['nItems'])

        Manager.create_new_user_session(key)

        print(f"audio_data: {audio_data}")
        print(f"key: {key}")
        output_file = f"{key}_recording.wav"
        
        audio_data.save(output_file)
        file = wave.open(output_file)
        framerate = file.getframerate()
        print(f"len: {file.getnframes()}")
        print(f"framerate: {framerate}")
        file.close()
        if framerate!=8000:
            audio = AudioSegment.from_wav(output_file)
            resampled_audio = audio.set_frame_rate(8000)
            resampled_audio.export(output_file, format='wav')
            file = wave.open(output_file)
            framerate = file.getframerate()
            print(f"After resample len: {file.getnframes()}")
            print(f"After resample framerate: {framerate}")
            if file.getnframes()<8000*2:
                Manager.write_data(key,"error",{"error":"Music should be longer than 2 seconds"})
                os.remove(output_file)
                return "Music should be longer than 2 seconds"
            file.close()
        
        Manager.set_status_user_session(key,"working")
        new_thread = threading.Thread(target=model_predict, args=(key,output_file,nItems,predict,Manager,search_music_info))
        thread_control.append(new_thread)
        new_thread.start()
        # model_predict(key,output_file,nItems,predict,Manager)
        return "Successfully"
    except Exception as e:
        Manager.write_data(key,"error",{"error":str(e)})
        print(f"Error: {e}")
        return "An error occurred"

@main.route('/check-server-status',methods=["GET"])
def check_server_status():
    return jsonify({"server_status":"ready"})

@main.route('/')
def main_template():
    return "<h1>This is API Server</h1><p>Hello, World!</p>"
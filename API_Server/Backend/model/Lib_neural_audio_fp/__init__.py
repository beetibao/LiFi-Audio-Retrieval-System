from .model_core.fp.melspec.melspectrogram import get_melspec_layer
from .model_core.fp.nnfp import get_fingerprinter

from .class_base import Model,Search_Engine
import yaml, os, wave, faiss, pathlib
import numpy as np
import pandas as pd
from tqdm import tqdm
import tensorflow as tf
import platform

os_name = platform.system()
model_ver = "fp_model_v5"
model_data_path = r"Backend\model\Lib_neural_audio_fp\model_data"

def get_path(path):
    if os_name == "Linux": return path.as_posix()
    return path

def get_config():
    config_path = pathlib.PureWindowsPath(rf"{model_data_path}\default.yaml")
    config_path = os.path.join(os.getcwd(),get_path(config_path))
    # print("get_config has been called")
    # print(f"'{config_path}' exists: {os.path.exists(config_path)}")
    return yaml.safe_load(open(config_path,"r"))

cfg = get_config()

def get_model():
    model_path = pathlib.PureWindowsPath(rf"{model_data_path}\{model_ver}\ckp")
    model_path = os.path.join(os.getcwd(),get_path(model_path))

    m_pre = get_melspec_layer(cfg, trainable=False)
    
    # print("get_config has been called")
    # print(f"'{model_path}' exists: {os.path.exists(model_path)}")
    # m_fp = tf.saved_model.load(model_path)
    m_fp = get_fingerprinter(cfg, trainable=True)
    
    checkpoint = tf.train.Checkpoint(model=m_fp)

    # checkpoint_dir = "/kaggle/input/neural-audio-fp/checkpoints/640_lamb"
    checkpoint_dir = model_path

    c_manager = tf.train.CheckpointManager(checkpoint, checkpoint_dir, max_to_keep=None)
    latest_checkpoint = c_manager.latest_checkpoint
    # print(f"last_checkpoint: {latest_checkpoint}")
    checkpoint.restore(latest_checkpoint)

    return Model(m_fp,m_pre)

def load_db(source_dir,name):
    db_shape = np.load(os.path.join(source_dir,name+"_shape.npy"))
    db = np.memmap(os.path.join(source_dir,name+".mm"), 
                   dtype='float32', mode='r',
                   shape=(db_shape[0], db_shape[1]))
    return db_shape,db

def get_search_engine():
    # database_path = r"backend\Lib_neural_audio_fp\fp_model\Database"
    # database_path = os.path.join(os.getcwd(),database_path)
    # _,db = load_db(database_path,"custom_source")
    just_index = pathlib.PureWindowsPath(rf"{model_data_path}\{model_ver}\index.faiss")
    just_index = os.path.join(os.getcwd(),get_path(just_index))
    index = faiss.read_index(just_index)

    info_dataframe_path = pathlib.PureWindowsPath(rf"{model_data_path}\{model_ver}\info_df.csv")
    info_dataframe_path = os.path.join(os.getcwd(),get_path(info_dataframe_path))
    info_df = pd.read_csv(info_dataframe_path)

    music_info_path = pathlib.PureWindowsPath(rf"{model_data_path}\{model_ver}\Music_Info.csv")
    music_info_path = os.path.join(os.getcwd(),get_path(music_info_path))
    music_info = pd.read_csv(music_info_path)

    return Search_Engine(index,info_df,music_info,load_just_SO=True)

    


def encode_query(audio_query_file,model,
                duration=int(cfg["MODEL"]["DUR"]),
                hop=cfg["MODEL"]["HOP"],
                fs=int(cfg["MODEL"]["FS"])):
    # print("Start encoding")
    assert os.path.exists(audio_query_file), f"{audio_query_file} does not exist"
    assert 0<hop<=duration, f"Hop size must be between 0 and {duration}"
    file = wave.open(audio_query_file)
    assert fs==file.getframerate()
    
    n_frames_in_seg = fs * duration
    n_frames_in_hop = fs * hop
    
    n_frames = file.getnframes()
    # print(f"encode_query n_frames: {n_frames}")
    n_seg = int((n_frames - n_frames_in_seg) // n_frames_in_hop)
    last = int(n_frames-(n_seg*n_frames_in_hop+n_frames_in_seg))
    # print(f"encode_query n_seg: {n_seg}")
    # print(f"encode_query last: {n_frames-(n_seg*n_frames_in_hop+n_frames_in_seg)}")
    
    seg_queries = []
    for seg in tqdm(range(n_seg),):
        file.setpos(int(seg*n_frames_in_hop))
        data = file.readframes(n_frames_in_seg)
        data = np.frombuffer(data,dtype=np.int16)/2**15
        seg_queries.append(data.tolist())
    if last!=0:
        file.setpos(int(n_seg*n_frames_in_hop))
        data = file.readframes(last)
        data = np.frombuffer(data,dtype=np.int16)/2**15
        add = np.zeros(n_frames_in_seg - last).tolist()
        data = data.tolist()
        data.extend(add)
        seg_queries.append(data)
    file.close()
    out = np.array(seg_queries).reshape(-1,1,8000*duration)
    # print(f"Before model - encode shape: {out.shape}")
    out = model(out).numpy()
    # print(f"After model - encode shape: {out.shape}")
    return out
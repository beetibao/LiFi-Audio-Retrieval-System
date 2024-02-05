from .Lib_neural_audio_fp import encode_query, get_model, get_search_engine

class MainModel:
    def __init__(self):
        print("Load audio encoding model",end="")
        self.fp_model = get_model()
        print(" --> Done")

        print("Load search engine",end="")
        self.search_engine = get_search_engine()
        print(" --> Done")

    def search(self,audio_file,k,just_best_item,**kwargs):
        query = encode_query(audio_file, self.fp_model,**kwargs)
        # print(f"MainModel search query encoding shape: {query}")
        return self.search_engine.search(query,k,just_best_item)

__model = MainModel()

def search_music_info(name):
    return __model.search_engine.search_info_music(name)

def predict(audio_file,k=20,suggest_list=True,**kwargs):
    # model = MainModel()
    
    # engine_file = os.path.join(os.getcwd(),"backend\Lib_neural_audio_fp\search_engine_2.model")
    # engine = get_search_engine() #joblib.load(engine_file)
    # query = encode_query(audio_file, model)

    return __model.search(audio_file,k,just_best_item=(not suggest_list),**kwargs)

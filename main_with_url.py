#-----------install librairies--------------

import os
import pandas as pd
from datetime import datetime
import random
import numpy as np
import multiprocessing as mp
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from utils_radio import download_audio, transcript
import warnings
warnings.filterwarnings("ignore")

#-----------PIPELINE-----------------------

#DOWNLOAD AUDIO FROM URL, MAKE TRANSCRIPTION, DELETE AUDIO
MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-french"
processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID)

df_url = pd.read_csv("./7-9_URLs.csv", delimiter = ",", header = 0)

def main_with_url(i):
    i = i-32
    if (i%5) == 0:
        r = random.randint(0, 4)
        i += r
    else:
        return

    audio_url = df_url["URL"][i]
    date = str(audio_url[54:64])
    date_obj = datetime.strptime(date, "%d.%m.%Y")
    date = int(date_obj.timestamp())
    id = i
    titre = "inconnu"
    df_trans = pd.read_csv("./transcript.csv", delimiter = ",", header = 0)
    if date in df_trans["Date"].values:
        index_trans = df_trans.loc[df_trans["Date"] == date].index[0]
        if not pd.isnull(df_trans.loc[index_trans, 'Transcript']):
            return
    
    #make transcription
    print("transcription: start")
    if str(id)+'.mp3' not in os.listdir('./audios'):
        download_audio(str(id), str(audio_url)) #download in audios folder
    audio_file = "./audios/"+str(id)+".mp3"
    text = transcript(audio_file, processor, model)
    #reload to be sure to have the last version
    df_trans = pd.read_csv("./transcript.csv", delimiter = ",", header = 0)
    if date in df_trans["Date"].values:
        index_trans = df_trans.loc[df_trans["Date"] == date].index[0]
        df_trans.loc[index_trans, 'Transcript'] = text
    else :
        new_row = {'Id': id, 'Titre': titre, 'Date': date, 'Url': audio_url, 'Transcript': text}
        df_trans = df_trans.append(new_row, ignore_index=True)
    index_trans = df_trans.loc[df_trans["Date"] == date].index[0]
    df_trans.to_csv('./transcript.csv', index=False)

    #delete old audios
    if (not pd.isnull(df_trans.loc[index_trans, 'Transcript'])) and (str(id)+'.mp3' in os.listdir('./audios')):
        os.remove("./audios/"+str(id)+'.mp3')
    print(70*"=")


all_index = np.arange(32, 1488)
num_processes = 20
with mp.Pool(num_processes) as pool:
    results = pool.map(main_with_url, all_index)
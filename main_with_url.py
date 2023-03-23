#-----------install librairies--------------

import os
import pandas as pd
from datetime import datetime
import random
import numpy as np
import multiprocessing as mp
import collections
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

def transcription(index):
    i = index
    audio_url = df_url["URL"][i]
    date = str(audio_url[54:64])
    date_obj = datetime.strptime(date, "%d.%m.%Y")
    date = int(date_obj.timestamp())
    titre = "inconnu"
    id = i
    print("transcription: start")
    if str(id)+'.mp3' not in os.listdir('./audios'):
        download_audio(str(id), str(audio_url)) #download in audios folder
    audio_file = "./audios/"+str(id)+".mp3"
    text = transcript(audio_file, processor, model)
    print("transcription: end")
    return {'Id' : id, 'Titre': titre, 'Date': date, 'Url': audio_url, 'Transcript': text}

def transcription_on_list(batch_list):
    output_dict = collections.defaultdict()
    for batch in batch_list:
        output_dict[batch] = transcription(batch)
    #save it in csv
    my_dict = dict(output_dict)
    df = pd.DataFrame(my_dict)
    df = df.transpose()
    df.to_csv('./saves/'+str(batch)+'.csv', index=False)
    return output_dict

all_index = np.arange(32, 1488)
all_my_batches = []
for index in all_index:
    i = index-32
    if (i%5) == 0:
        r = random.randint(0, 4)
        i += r
        all_my_batches.append(i)

### MultiProcess approach :
# We start by creating sub list of batches, here 30 sub list
splitted_target = np.array_split(all_my_batches, 20)
# Here we use 20 processes in the pool
sub_pool = mp.Pool(processes=20)
sub_results = sub_pool.starmap(transcription_on_list, zip(splitted_target))
sub_pool.close()
sub_pool.join()

# Now we collect the final result using sub_results, a list 

final_dict = collections.defaultdict()
for baby_dict in sub_results:
    try:
        final_dict.update(baby_dict)
    except:
        pass

my_final_dict = dict(final_dict)
df_tot = pd.DataFrame(my_final_dict)
df_tot = df_tot.transpose()
df_tot.to_csv('./saves/final_df.csv', index=False)
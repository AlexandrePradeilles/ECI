#-----------install librairies--------------

import os
import pandas as pd
from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from utils_radio import store_data_radio, download_audio, transcript
import warnings
warnings.filterwarnings("ignore")

#-----------PIPELINE-----------------------

#CONNEXION API RADIO FRANCE
# Initialize connexion
#print("call API: start")
#transport = AIOHTTPTransport(url="https://openapi.radiofrance.fr/v1/graphql?x-token=36bee04f-68a9-4bf8-8f2c-0662b454192c")
#client = Client(transport=transport, fetch_schema_from_transport=True)
#return id, titre, date, url
#url = "https://www.radiofrance.fr/franceinter/podcasts/le-7-9"
#first = 40
#df_query = store_data_radio(client, url, first)
#df_query.to_csv('./query.csv', index=False)
#print("call API: done")

#DOWNLOAD AUDIO FROM URL, MAKE TRANSCRIPTION, DELETE AUDIO
MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-french"
processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID)

df_trans = pd.read_csv("./transcript.csv", delimiter = ",", header = 0)

#for i in range (df_query.shape[0]):
#    id, titre, date, audio_url = df_query.iloc[i]['Id'], df_query.iloc[i]['Titre'], df_query.iloc[i]['Date'], df_query.iloc[i]['Url']
#    #test if the audio is already transcripted
#    if id in df_trans["Id"].values:
#        index_trans = df_trans.loc[df_trans["Id"] == id].index[0]
#        if not pd.isnull(df_trans.loc[index_trans, 'Transcript']):
#            continue
    
#    #make transcription
#    print("transcription: start")
#    if str(id)+'.mp3' not in os.listdir('./audios'):
#        download_audio(str(id), str(audio_url)) #download in audios folder
#    audio_file = "./audios/"+str(id)+".mp3"
#    text = transcript(audio_file, processor, model)
    
#    if id in df_trans["Id"].values:
#        index_trans = df_trans.loc[df_trans["Id"] == id].index[0]
#        df_trans.loc[index_trans, 'Transcript'] = text
#    else :
#        new_row = {'Id': id, 'Titre': titre, 'Date': date, 'Url': audio_url, 'Transcript': text}
#        df_trans = df_trans.append(new_row, ignore_index=True)
#    index_trans = df_trans.loc[df_trans["Id"] == id].index[0]
#    df_trans.to_csv('./transcript.csv', index=False)

    #delete old audios
#    if (not pd.isnull(df_trans.loc[index_trans, 'Transcript'])) and (str(id)+'.mp3' in os.listdir('./audios')):
#        os.remove("./audios/"+str(id)+'.mp3')
#    print(70*"=")
#    print("Audios: {:.2f}%".format(100*i/df_query.shape[0]))



manual_query = [["fd74081d-f27d-4189-8fb8-87cb1ab9163c_1", "Nicole Bacharan - Sébastien Chenu - Laure Adler", 1676268000, "https://media.radiofrance-podcast.net/podcast09/10241-13.02.2023-ITEMA_23286603-2023F10761S0044-22.mp3"], 
                ["45d2e463-fae8-42d0-9f02-1a43e8c24452_1", "Débat économique sur les superprofits - Sylvie Kauffmann et Thomas Gomart - Bruno Fron", 1676008800, "https://media.radiofrance-podcast.net/podcast09/10241-10.02.2023-ITEMA_23284342-2023F10761S0041-22.mp3"], 
                ["3cdee815-2021-4f68-a998-6f0a137b0bc3_1", "Bernard Guetta - Rima Abdul Malak - Arnaud Fraisse et Rony Brauman", 1675922400, "https://media.radiofrance-podcast.net/podcast09/10241-09.02.2023-ITEMA_23283100-2023F10761S0040-22.mp3"], 
                ["55b972d9-043d-46b8-92a6-37eeafecef99_1", "Françoise Fressoz et Edouard Lecerf - Gérard Larcher - Patrick Bruel ", 1675836000, "https://media.radiofrance-podcast.net/podcast09/10241-08.02.2023-ITEMA_23281897-2023F10761S0039-22.mp3"]]

for data in manual_query:
    id, titre, date, audio_url = data
    if id in df_trans["Id"].values:
        index_trans = df_trans.loc[df_trans["Id"] == id].index[0]
        if not pd.isnull(df_trans.loc[index_trans, 'Transcript']):
            continue
    
    #make transcription
    print("transcription: start")
    if str(id)+'.mp3' not in os.listdir('./audios'):
        download_audio(id, audio_url) #download in audios folder
    audio_file = "./audios/"+id+".mp3"
    text = transcript(audio_file, processor, model)
    
    if id in df_trans["Id"].values:
        index_trans = df_trans.loc[df_trans["Id"] == id].index[0]
        df_trans.loc[index_trans, 'Transcript'] = text
    else :
        new_row = {'Id': id, 'Titre': titre, 'Date': date, 'Url': audio_url, 'Transcript': text}
        df_trans = df_trans.append(new_row, ignore_index=True)
    index_trans = df_trans.loc[df_trans["Id"] == id].index[0]
    df_trans.to_csv('./transcript.csv', index=False)

    #delete old audios
    if (not pd.isnull(df_trans.loc[index_trans, 'Transcript'])) and (id+'.mp3' in os.listdir('./audios')):
        os.remove("./audios/"+id+'.mp3')
    print(70*"=")
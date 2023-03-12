#-----------install librairies--------------

import os
import pandas as pd
from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from utils_radio import store_data_radio, download_audio, transcript

#-----------PIPELINE-----------------------

#CONNEXION API RADIO FRANCE
# Initialize connexion
transport = AIOHTTPTransport(url="https://openapi.radiofrance.fr/v1/graphql?x-token=36bee04f-68a9-4bf8-8f2c-0662b454192c")
client = Client(transport=transport, fetch_schema_from_transport=True)
#return id, titre, date, url
url = "https://www.radiofrance.fr/franceinter/podcasts/le-7-9"
df = store_data_radio(client, url)
df.to_csv('./url_7-9.csv', index=False)

#DOWNLOAD AUDIO FROM URL, MAKE TRANSCRIPTION, DELETE AUDIO
MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-french"
processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID)
df['Transcript'] = pd.Series(dtype='string')

for i in range (df.shape[0]):
    id, audio_url = df.loc[i, 'Id'], df.loc[i, 'Url']
    if str(id)+'.mp3' not in os.listdir('./audios'):
        download_audio(str(id), str(url)) #download in audios folder
    if pd.isnull(df.loc[i, 'Transcript']) :
        audio_file = "./audios/"+str(id)+".mp3"
        text = transcript(audio_file, processor, model) #make transcription
        df.loc[i, 'Transcript'] = text
        df.to_csv('./url_7-9.csv', index=False)
    if (not pd.isnull(df.loc[i, 'Transcript'])) and (str(id)+'.mp3' in os.listdir('./audios')):
        os.remove("./audios/"+str(id)+'.mp3') #delete old audios
#-----------install librairies--------------

import os
import pandas as pd
from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
import librosa
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

#DOWNLOAD AUDIO FROM URL
for i in range (df.shape[0]):
    id, audio_url = df.loc[i, 'Id'], df.loc[i, 'Url']
    if str(id)+'.mp3' not in os.listdir('./audios'):
        download_audio(id, url) #download in audios folder

#TRANSCRIPTION
MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-french"
processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID)

df['Transcript'] = pd.Series(dtype='string')
for i in range(df.shape[0]):
    if df.loc[i, 'Transcript'] == "":
        id = df.ID.iloc[i]
        audio_file = "./audios/"+str(id)+".mp3"
        speech_array, sr = librosa.load(audio_file, sr=16_000)
        text = transcript(speech_array, processor, model)
        df.loc[i, 'Transcript'] = text
        df.to_csv('./url_7-9.csv', index=False)
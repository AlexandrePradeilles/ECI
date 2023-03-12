#-----------install librairies--------------

#pip install huggingsound

import pandas as pd
import wget
import torch
from gql import gql
from mutagen.mp3 import MP3
import librosa
import numpy as np
import soundfile as sf
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


#-----------CONNEXION API RADIO FRANCE---------------



def query_podcast(url):
    """
    input: select the radio you want to hear, start and end determine the time during which we look for audio
    output: the query formated, ready to be use
    """
    query = gql(
        """
    {
        showByUrl(
            url: "%s"
        ) {
            diffusionsConnection {
                edges {
                    node {
                        id
                        title
                        published_date
                        podcastEpisode {
                            url
                            title
                        }
                    }
                }
            }
        }
    }
    """ %url
    )
    return query

def store_data_radio(client, url):
    """
    create a dataframe of radio between start and end, with title, resume, date, url, duration
    input: start and end, defining the time window of study
    output: a dataframe with all information needed
    """
    First_iter = True
    query = query_podcast(url)
    result = client.execute(query)
    data = result["showByUrl"]["diffusionsConnection"]["edges"]
    for i in range(len(data)):
        #tester s'il y a des émissions
        if data[i] == {}:
            continue
        #tester s'il y a l'audio
        if data[i]["node"]["podcastEpisode"] == None:
            continue

        id = data[i]["node"]["id"]
        titre_emi = data[i]["node"]["title"]
        date = data[i]["node"]["published_date"]
        url = data[i]["node"]["podcastEpisode"]["url"]
        info = [id, titre_emi, date, url]

        if First_iter :
            info = [info]
            df = pd.DataFrame(info, columns = ['Id','Titre','Date', 'Url'])
            First_iter = False
        else :
            df.loc[len(df)] = info

    return df

#--------------DOWNLOAD AUDIO FROM URL----------

def download_audio(id, url):
    """
    take an url, download it in the audios folder, with the id as name
    """
    wget.download(url, "./audios/"+str(id)+".mp3")


#--------------TRANSCRIPTION WITH WAVE2VEQ 2--------------

def transcript (audio_file, processor, model, sr = 44100, frames = 30*44100, len_recouvrement = 5):
    """
    return the transcription of a speech_array, with a step of 30s
    """
    audio = MP3(audio_file)
    duration = audio.info.length
    First_transcript = True
    text = ""
    start = 0
    while start+frames < sr*duration :
        if First_transcript:
            start = 0
            First_transcript = False
        else :
            start += frames - sr*len_recouvrement
        speech_array, sampling_rate = sf.read(audio_file, frames = frames, start = start)
        speech_array = speech_array.T
        speech_array = librosa.resample(np.asarray(speech_array), sampling_rate, 16_000)
        input_values = processor(speech_array, sampling_rate=16_000, return_tensors="pt", padding=True).input_values
        logits = model(input_values[0]).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        predicted_sentences = processor.batch_decode(predicted_ids)[0]
        text += predicted_sentences + " "

    if First_transcript:
        start = 0
    else :
        start += frames - sr*len_recouvrement
    speech_array, sampling_rate = sf.read(audio_file, start = start, stop = sr*duration)
    speech_array = speech_array.T
    speech_array = librosa.resample(np.asarray(speech_array), sampling_rate, 16_000)
    input_values = processor(speech_array, sampling_rate=16_000, return_tensors="pt", padding=True).input_values
    logits = model(input_values[0]).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    predicted_sentences = processor.batch_decode(predicted_ids)[0]
    text += predicted_sentences
    
    return text
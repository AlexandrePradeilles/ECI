#-----------install librairies--------------

#pip install huggingsound

import pandas as pd
import wget
import torch
from gql import gql


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
    response = wget.download(url, "./audios/"+str(id)+".mp3")


#--------------TRANSCRIPTION WITH WAVE2VEQ 2--------------

def transcript (speech_array, processor, model, sr = 16_000, pas = 30, len_recouvrement = 5):
    """
    return the transcription of a speech_array, with a step of 30s
    """
    i = 0
    stop_time = 0
    text = ""
    while int((stop_time+pas-len_recouvrement)*sr) < len(speech_array):
        if i == 0:
            start_time = i*pas
        else :
            start_time = i*pas - len_recouvrement
        stop_time = start_time+pas
        start_sample = int(start_time * sr)
        stop_sample = int(stop_time * sr)
        short_speech_array = speech_array[start_sample:stop_sample]
        
        input = processor(short_speech_array, sampling_rate=16_000, return_tensors="pt", padding=True)

        with torch.no_grad():
            logits = model(input.input_values, attention_mask=input.attention_mask).logits

        predicted_ids = torch.argmax(logits, dim=-1)
        predicted_sentences = processor.batch_decode(predicted_ids)[0]
        text += predicted_sentences + " "
        i+=1
    
    start_time += pas - len_recouvrement
    start_sample = int(start_time * sr)
    stop_sample = len(speech_array)
    short_speech_array = speech_array[start_sample:stop_sample]
    input = processor(short_speech_array, sampling_rate=16_000, return_tensors="pt", padding=True)
    with torch.no_grad():
        logits = model(input.input_values, attention_mask=input.attention_mask).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    predicted_sentences = processor.batch_decode(predicted_ids)
    text += predicted_sentences
    return text


#transcript (speech_array)
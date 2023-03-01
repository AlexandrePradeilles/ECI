#pip install huggingsound

import pandas as pd
import wget
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from huggingsound import SpeechRecognitionModel


#-----------RETURN radio, titre_emi, resume, date, url, duration---------------

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url="https://openapi.radiofrance.fr/v1/graphql?x-token=36bee04f-68a9-4bf8-8f2c-0662b454192c")

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

#liste de radios
#liste_radio = ["FRANCEINFO", "FRANCEINTER", "FRANCEMUSIQUE", "FRANCECULTURE", "MOUV", "FIP", "FRANCEBLEU"]
liste_radio = ["FRANCEINFO", "FRANCEINTER", "FRANCECULTURE", "FRANCEBLEU"]


def query_podcast(radio, start, end):
    query = gql(
        """
    {
        grid(
            start: %s
            end: %s
            station: %s
            includeTracks: false
        ) {
            ... on DiffusionStep {
                diffusion {
                    title
                    standFirst
                    published_date
                    podcastEpisode {
                        url
                        duration
                    }
                }
            }
        }
    }
    """ %(start, end, radio)
    )
    return query

def store_data_radio(start, end):
    First_iter = True
    t=0
    for radio in liste_radio:
        query = query_podcast(radio, start, end)
        result = client.execute(query)

        for i in range(len(result["grid"])):
            #tester s'il y a des émissions
            if result["grid"][i] == {}:
                continue
            #tester s'il y a informations
            if result["grid"][i]["diffusion"] == None:
                continue
            #tester s'il y a l'audio
            if result["grid"][i]["diffusion"]["podcastEpisode"] == None:
                continue

            titre_emi = result["grid"][i]["diffusion"]["title"]
            resume = result["grid"][i]["diffusion"]["standFirst"]
            date = result["grid"][i]["diffusion"]["published_date"]
            url = result["grid"][i]["diffusion"]["podcastEpisode"]["url"]
            duration = result["grid"][i]["diffusion"]["podcastEpisode"]["duration"]
            info = [radio, titre_emi, resume, date, url, duration]

            if First_iter :
                info = [info]
                df = pd.DataFrame(info, columns = ['Radio','Titre','Resume', 'Date', 'Url', 'Durée'])
                First_iter = False
            else :
                df.loc[len(df)] = info

            t+=1
            if t%10==0:
                print(t)

    return df


start = "1673910000" #17/01/2023 00h00
end = "1673996400" #18/01/2023 00h00
df = store_data_radio(start, end)
print(df.head())
print(df.shape)

df.to_csv('./emissions_radio.csv', index=False)


#--------------DOWNLOAD AUDIO FROM URL----------

def download_audio(url):
    """
    take an url, download it in the current folder
    """
    response = wget.download(url, "emission_1.mp3")

#--------------TRANSCRIPTION WITH WAVE2VEQ--------------

model = SpeechRecognitionModel("jonatasgrosman/wav2vec2-large-xlsr-53-french")

audio_paths = ["C://Users//antoi//OneDrive//Bureau//CS//3A//ProjetEleven//radiomp3_court.mp3"]

transcriptions = model.transcribe(audio_paths)[0]
print(transcriptions["transcription"])
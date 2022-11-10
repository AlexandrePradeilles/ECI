from huggingsound import SpeechRecognitionModel

model = SpeechRecognitionModel("jonatasgrosman/wav2vec2-large-xlsr-53-french")
audio_paths = ["C:\\Users\\antoi\\OneDrive\\Bureau\\CS\\3A\\ProjetEleven\\TestWav.wav"]

transcriptions = model.transcribe(audio_paths)
print(transcriptions["transcription"]) #renvoi le texte = transcription, les strart_timestamps, end_timestamps, probabilities
import torch
import librosa
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import soundfile as sf

MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-french"
audio_file = "TestWav.wav"

processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID)

# speech, rate = sf.read("test_intro.mp3")
# speech_array = librosa.resample(speech.T, rate, 16000)

# print("now")
speech_array, _ = librosa.load(audio_file, sr=16_000)

input = processor(speech_array, sampling_rate=16_000, return_tensors="pt", padding=True)

with torch.no_grad():
    logits = model(input.input_values, attention_mask=input.attention_mask).logits

predicted_ids = torch.argmax(logits, dim=-1)
predicted_sentences = processor.batch_decode(predicted_ids)

print(predicted_sentences)


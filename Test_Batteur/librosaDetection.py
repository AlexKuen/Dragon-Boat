import aubio
import numpy as num
import pyaudio
import audioop
import librosa

# PyAudio object.
p = pyaudio.PyAudio()

win_s = 1024                # fft size
hop_s = win_s // 2          # hop size
samplerate = 44100

# Open stream.
stream = p.open(format=pyaudio.paFloat32,
    channels=1, rate=samplerate, input=True,
    frames_per_buffer=hop_s)


counter = 0
while True:

    data = stream.read(hop_s)
    samples = num.frombuffer(data, dtype=aubio.float_type)


    tempo, beats = librosa.beat.beat_track(y=samples, sr=samplerate, hop_length=hop_s)
    volume = audioop.rms(data, 2) 
    
    if volume > 10000 :
        print("tempo :", tempo)
        print("beats :", beats)
    

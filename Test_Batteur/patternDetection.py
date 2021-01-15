from scipy.io.wavfile import read
import aubio
import numpy as num
import pyaudio

def calc_distances(data, fs):
    #The minimun value for the sound to be recognized as a knock
    min_val = 5000
    
    data_size = len(data)
    
    #The number of indexes on 0.15 seconds
    focus_size = int(0.15 * fs)
    
    focuses = []
    distances = []
    idx = 0
    
    while idx < len(data):
        print("data : ", data[idx])
        if data[idx] > min_val:
            mean_idx = idx + focus_size // 2
            focuses.append(float(mean_idx) / data_size)
            if len(focuses) > 1:
                last_focus = focuses[-2]
                actual_focus = focuses[-1]
                distances.append(actual_focus - last_focus)
            idx += focus_size
        else:
            idx += 1
    return distances

def accept_test(pattern, test, min_error):
    if len(pattern) > len(test):
        return False
    for i, dt in enumerate(pattern):
        if not dt - test[i] < min_error:
            return False
    return True

# the minimum difference between the patterns in seconds
min_error = 0.1

# PyAudio object.
p = pyaudio.PyAudio()

win_s = 2048                # fft size
hop_s = win_s // 2          # hop size
samplerate = 44100

# Open stream.
stream = p.open(format=pyaudio.paFloat32,
    channels=1, rate=samplerate, input=True,
    frames_per_buffer=hop_s)


a_tempo = aubio.tempo("default", win_s, hop_s, samplerate)

#a_pitch = aubio.pitch("yin", samplerate)

fs, toc = read('tap.wav')

#pattern = calc_distances(toc, win_s)
    
counter = 0
while counter == 0:

    data = stream.read(hop_s)
    samples = num.frombuffer(data, dtype=aubio.float_type)
    
    test = calc_distances(samples, win_s)
    """
    if accept_test(pattern, test, min_error):
        counter += 1
        print(counter)
        """
    print(test)
    counter = 1



import sounddevice as sd
import numpy as np
import scipy.signal
import timeit
import python_speech_features
from queue import Queue
import tensorflow as tf

from pydub.playback import play
from pydub import AudioSegment
import sounddevice as sd
import soundfile as sf
import datetime
import os
from audio import stt
window_stride = 0.5
song = AudioSegment.from_mp3("./res/sound.mp3")

class Listener:
    def __init__(self):
        self.queue = Queue
        self.sample_rate = 48000
        self.rec_duration = 0.5
        self.resample_rate = 8000
        # Sliding self.window
        self.window = np.zeros(int(self.rec_duration * self.resample_rate) * 2)

        self.word_threshold = 0.1
        self.debug_time = 1
        self.debug_acc = 0

        self.num_mfcc = 16

        # Load model (interpreter)
        model_path = 'wake_word_yes_lite.tflite'
        self.interpreter = tf.lite.Interpreter(model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        # print(input_details)

        self.now = datetime.datetime.now() # 녹화 시작 시간
        self.output_path = './res/voice/' + self.now.strftime("%Y-%m-%d_%H:%M:%S") + '.wav'
        self.fs = 16000
        self.seconds = 3

        self.command = ''

    # Decimate (filter and downsample)
    def decimate(self, signal, old_fs, new_fs):
        
        # Check to make sure we're downsampling
        if new_fs > old_fs:
            print("Error: target sample rate higher than original")
            return signal, old_fs
        
        # We can only downsample by an integer factor
        dec_factor = old_fs / new_fs
        if not dec_factor.is_integer():
            print("Error: can only decimate by integer factor")
            return signal, old_fs

        # Do decimation
        resampled_signal = scipy.signal.decimate(signal, int(dec_factor))

        return resampled_signal, new_fs

    # This gets called every 0.5 seconds
    def sd_callback(self, rec, frames, time, status):
        # Start timing for testing
        start = timeit.default_timer()
        
        # Notify if errors
        if status:
            print('Error:', status)
        
        # Remove 2nd dimension from recording sample
        rec = np.squeeze(rec)
        
        # Resample
        rec, new_fs = self.decimate(rec, self.sample_rate, self.resample_rate)
        
        # Save recording onto sliding window
        self.window[:len(self.window)//2] = self.window[len(self.window)//2:]
        self.window[len(self.window)//2:] = rec

        # Compute features
        mfccs = python_speech_features.base.mfcc(self.window, 
                                            samplerate=new_fs,
                                            winlen=0.256,
                                            winstep=0.050,
                                            numcep=self.num_mfcc,
                                            nfilt=26,
                                            nfft=2048,
                                            preemph=0.0,
                                            ceplifter=0,
                                            appendEnergy=False,
                                            winfunc=np.hanning)
        mfccs = mfccs.transpose()

        # Make prediction from model
        in_tensor = np.float32(mfccs.reshape(1, mfccs.shape[0], mfccs.shape[1], 1))
        self.interpreter.set_tensor(self.input_details[0]['index'], in_tensor)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        val = output_data[0][0]
        if val > 0.1:
            print('yes')
            print('== start recording ==')
            myrecording = sd.rec(int(self.seconds * self.fs), samplerate=self.fs, channels=1, dtype='int16')
            play(song) # 효과음

            sd.wait() # wait until recording is finished

            sf.write(self.output_path, myrecording, self.fs)
            print('== end recording ==')
            self.command = self.get_command()


        if self.debug_acc:
            print(val)
        
        if self.debug_time:
            print(timeit.default_timer() - start)
    

    # Get the full phrase from the listener
    def get_command(self):
        command = ''

        with open(self.output_path, 'rb') as fp:
        # with open('heykakao.wav', 'rb') as fp:
            audio = fp.read()

        command = stt(audio)

        print(f'get_command @ {command}')
        os.remove(self.output_path)
        return command

    def run(self):
        num_channels = 1
        # Start streaming from microphone
        with sd.InputStream(channels=num_channels,
                            samplerate=self.sample_rate,
                            blocksize=int(self.sample_rate * self.rec_duration),
                            callback=self.sd_callback):
            while True:
                if self.command:
                    return self.command
                # pass
                # key = self.queue.get()
                # if key == True:
                #     break

if __name__=="__main__":
    listener = Listener()
    listener.run()
#!/usr/bin/env python3
import tempfile
import queue
import threading
import signal
import sounddevice as sd
import soundfile as sf
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy  # avoid "imported but unused" message (W0611)
from styles import Style
import whisper
import os
from yaspin import yaspin
import cmd2

class AudioManager(cmd2.Cmd):
    def __init__(self, samplerate=44100, channels=2, device=None,subtype=None):
        super().__init__()
        self.samplerate = samplerate
        self.channels = channels
        self.device = device
        self.filename = tempfile.mktemp(prefix='rec_', suffix='.wav', dir='cache')
        self.subtype = subtype
        self.q = queue.Queue()
        self.recording = False
        self.recordedText = None 

        self.poutput(Style.INFO.style(f'AudioManager is created: samplerate={self.samplerate}, channels={self.channels}, device={self.device}, filename={self.filename}, subtype={self.subtype}'))

    def record(self):
        self.poutput(Style.IMPORTANT.style('Press Ctrl+C to stop the recording'))
        self.recording = True
        self.recordedText = None

        def callback(indata, frames, time, status):
            """This is called (from a separate thread) for each audio block."""
            if status:
                self.poutput(Style.ERROR.stye(status))
            self.q.put(indata.copy())

        with yaspin(text="Recording...", color="red") as sp:
            def signal_handler(sig, frame):       
                sp.ok("✔")                
                self.poutput(Style.IMPORTANT.style('\nCaught Ctrl+C. Stop recording...'))
                self.recording = False
                signal.signal(signal.SIGINT, signal.SIG_DFL)

                # whisper - speech recognition
                model = whisper.load_model("base")
                response = model.transcribe(os.getcwd() + '/' + self.filename)
                self.recordedText = response['text']
        
            signal.signal(signal.SIGINT, signal_handler)
            with sf.SoundFile(self.filename, mode='x', samplerate=self.samplerate,
                            channels=self.channels, subtype=self.subtype) as file:
                with sd.InputStream(samplerate=self.samplerate, device=self.device,
                                    channels=self.channels, callback=callback):
                                        
                    while self.recording:
                        file.write(self.q.get())
                    
                    return self.recordedText                
    def isRecording(self):
        return self.recording
    
    def getFilename(self):
        return self.filename
    
    def play(self, data):
        q = queue.Queue(maxsize=1024)
        event = threading.Event()

        def callback(outdata, frames, time, status):
            global current_frame
            if status:
                print(status)
            chunksize = min(len(data) - current_frame, frames)
            outdata[:chunksize] = data[current_frame:current_frame + chunksize]
            if chunksize < frames:
                outdata[chunksize:] = 0
                raise sd.CallbackStop()
            current_frame += chunksize    

        stream = sd.OutputStream(
            samplerate=self.samplerate, device=self.device, channels=data.shape[1],
            callback=callback, finished_callback=event.set)
        with stream:
            event.wait()  # Wait until playback is finished
        
    def stop(self):
        self.q.put(None)
        
from audio import AudioManager
from utils import display_image
from styles import Style
from chat import ChatBot
from modules.ChatTTS import ChatTTS
import soundfile as sf
import simpleaudio as sa
from yaspin import yaspin
import cmd2
from cmd2 import (
    Fg,
    style,
)
import time
from __init__ import __app_name__, _get_waiting_quotes
import argparse
from pypdf import PdfReader 
import filetype

class App(cmd2.Cmd):
    def __init__(self, env):
        super().__init__(allow_cli_args=False)
        self.prompt = '>>> '        
        self.env = env
        self.recording = False
        self.speaker = None

        # Hide unnecessary commands
        self.hidden_commands.append('macro')
        self.hidden_commands.append('run_pyscript')
        self.hidden_commands.append('run_script')
        self.hidden_commands.append('edit')
        
        with yaspin(text="Loading...", color="cyan") as sp:
            time.sleep(1)            
            # Setting can be saved 
            # self.model = model
            # self.set_tts(tts)
            # self.set_tts()
            self.chatBot = ChatBot(env_file=self.env)

        self.welcome()

    # Config
    cmd_parser = cmd2.Cmd2ArgumentParser(description='Config')
    cmd_parser.add_argument('-m', '--model', help='Name of the model')
    cmd_parser.add_argument('-t', '--tts', choices=['0', '1'], help='Enable/Disable TTS')

    @cmd2.with_category(__app_name__)
    @cmd2.with_argparser(cmd_parser)
    def do_config(self, args: argparse.Namespace):
        if args.model:
            self.model = args.model
            self.chatBot = ChatBot(env_file=self.env, model_name=self.model)
            self.poutput(Style.INFO.style('Model changed to {}'.format(self.model)))         

        # Check if tts value changed
        if args.tts: 
            if args.tts == '1' and self.speaker is None: 
                self.set_tts(True)
            elif args.tts == '0' and self.speaker is not None:   
                self.set_tts(False)                 

    def set_tts(self, enabled = False):
        if enabled:
            self.speaker = ChatTTS.Chat()
            self.poutput(Style.INFO.style('TTS enabled'))
        else:
            self.speaker = None
            self.poutput(Style.INFO.style('TTS disabled'))

    @cmd2.with_category(__app_name__)        
    def do_speak(self, text):
        recorded_text = self.record()
        self.poutput(style(recorded_text, fg=Fg.WHITE, dim=True, bold=True))  
        self.chat(recorded_text)

    do_say = do_speak

    @cmd2.with_category(__app_name__)
    def do_exit(self, line):
        self.poutput(Style.BOT.style('Bye!'))
        return True
    
    img_parser = cmd2.Cmd2ArgumentParser(description='Image')
    img_parser.add_argument('path', help='Path of the image file')

    @cmd2.with_argparser(img_parser)
    @cmd2.with_category(__app_name__)
    def do_image(self, args: argparse.Namespace):
        if args.path:
            # im = Image.open(args.path) 
            # im.show()
            display_image(args.path)
            prompt = self.read_input(
                Style.PROMPT.style('Input prompt for the image > '),
            )
            # TODO: to use image as prompt foe Vision api

    doc_parser = cmd2.Cmd2ArgumentParser(description='Add documents')
    doc_parser.add_argument('path', help='Path of the document file or document folder', completer=cmd2.Cmd.path_complete)

    @cmd2.with_argparser(doc_parser)
    @cmd2.with_category(__app_name__)
    def do_add(self, args: argparse.Namespace):
        # Load documents
        # TODO: Only support pdf file now
        if filetype.guess(args.path).mime == 'application/pdf':
            reader = PdfReader(args.path)
            pages = reader.pages
            for page in pages:
                self.poutput(page.extract_text())
                
        # Embedding
        # Vector database
        pass

    def default(self, statement):        
        # the argument will be passed here if app start with some arguments
        # TODO: need to ignore this!!!
        
        line = statement.raw
        if len(line) == 0:
            return
        
        self.chat(line)

    def chat(self, text):
        global say
        say = ''
        # self.poutput(Style.PROMPT.style('{}: '.format(self.chatBot.get_model_name())),end='')
        def chat_callback(stream):
            global say
            say += stream
            self.poutput(Style.BOT.style('{}'.format(stream)),end='')

        self.chatBot.chat(text, chat_callback)
        self.poutput(Style.BOT.style('\n'))
        # Streaming complete
        waiting = _get_waiting_quotes() + '...'
        with yaspin(text=waiting, color="cyan") as sp:
            if self.speaker:
                self.speaker.load(compile=True)
                wavs = self.speaker.infer(say)
                self.play(wavs)

    def welcome(self):
        status = 'enabled' if self.speaker else 'disabled'
        self.intro = Style.SYSTEM.style('Welcome to the {}! The model is {}. TTS is {}'.format(__app_name__, self.chatBot.get_model_name(), status))

    def record(self):         
        audioManger = AudioManager(channels=1) # Don't know why. channel = 1 will record stereo
        text = audioManger.record()  # This is a blocking call. May consider to make async

        self.poutput(Style.INFO.style('\nRecording stopped. fileName is {}'.format(audioManger.getFilename())))
        return text
        
    def play(self, wav):
        # audioManger = AudioManager(channels=1)
        # audioManger.play(wav)
        # TODO: This is a temp solution (using sound file)
        sf.write("temp.wav", wav[0][0], 24000)
        wave_obj = sa.WaveObject.from_wave_file('temp.wav')
        play_obj = wave_obj.play()
        play_obj.wait_done()  # Wait until sound has finished playing
        
    
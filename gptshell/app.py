import base64
import os
import pathlib
from PIL import Image
from audio import AudioManager
from gptshell.embedor import Embedor
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
from config import Config
from ollama import generate

class App(cmd2.Cmd):
    def __init__(self, env):
        super().__init__(allow_cli_args=False)
        self.prompt = '>>> '        
        self.env = env
        self.recording = False
        self.speaker = None
        self.embedor = Embedor()
        
        with yaspin(text="Loading...", color="cyan") as sp:
            time.sleep(1)            
            self.config = Config(env_file=self.env)
            model_name = self.config.get_model()
            self.chatBot = ChatBot(env_file=self.env,model_name=model_name)
            tts = self.config.get_tts()
            if tts:
                self.set_tts(True, silent=True)
            self.debug = self.config.get_debug()            
            self.set_debug(self.debug)

        self.remove_commands()
        self.welcome()

    # Build-in commands hooks
    def onecmd_plus_hooks(self, line):
        cmd_name, words, _ = self.parseline(line)
        args = words.split()
        if len(args) > 1:            
            if cmd_name == 'set':
                if args[0].lower() == 'debug':
                    if args[1].lower() == 'true':
                        return super().onecmd_plus_hooks('config -d 1')
                    else:
                        return super().onecmd_plus_hooks('config -d 0')                    

        return super().onecmd_plus_hooks(line)

    # Config
    cmd_parser = cmd2.Cmd2ArgumentParser(description='Config')
    cmd_parser.add_argument('-m', '--model', help='Name of the model')
    cmd_parser.add_argument('-t', '--tts', choices=['0', '1'], help='Enable/Disable TTS')
    cmd_parser.add_argument('-d', '--debug', choices=['0', '1'], help='Enable/Disable Debug')

    @cmd2.with_category(__app_name__)
    @cmd2.with_argparser(cmd_parser)
    def do_config(self, args: argparse.Namespace):
        if args.model:
            model = args.model
            self.chatBot = ChatBot(env_file=self.env, model_name=model)
            self.config.set_model(model)
            self.poutput(Style.INFO.style('Model changed to {}'.format(model)))         

        # Check if tts value changed
        if args.tts: 
            if args.tts == '1' and self.speaker is None: 
                self.set_tts(True)
                self.config.set_tts(True)
            elif args.tts == '0' and self.speaker is not None:   
                self.set_tts(False)           
                self.config.set_tts(False)        

        if args.debug:
            if args.debug == '1':
                self.set_debug(True)
                self.config.set_debug(True)
            elif args.debug == '0':
                self.set_debug(False)
                self.config.set_debug(False)
             
    def set_tts(self, enabled = False, silent = False):
        if enabled:
            self.speaker = ChatTTS.Chat()
            if not silent:
                self.poutput(Style.INFO.style('TTS enabled'))
        else:
            self.speaker = None
            if not silent:
                self.poutput(Style.INFO.style('TTS disabled'))

    def set_debug(self, enabled = True):
        # TODO: Trigger the system set debug from poutput, if there a better way?
        if enabled:
            self.debug = True
            self.poutput(Style.PROMPT.style('set debug True'))

        else:
            self.debug = False
            self.poutput(Style.PROMPT.style('set debug False'))

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
    
    img_parser = cmd2.Cmd2ArgumentParser(description='Add image as input')
    img_parser.add_argument('path', help='Path of the image file', completer=cmd2.Cmd.path_complete)

    @cmd2.with_argparser(img_parser)
    @cmd2.with_category(__app_name__)
    def do_image(self, args: argparse.Namespace):
        if args.path:
            im = Image.open(args.path) 
            im.show()
            # display_image(args.path)
            image_base64 = base64.b64encode(open(args.path, 'rb').read()).decode('utf-8')
            placeholder = 'Input prompt for the image'
            # input(f'>>> {placeholder}' + ('\b'*len(placeholder)))

            prompt = self.read_input(
                # Style.PROMPT.style(f'> {placeholder}' + ('\b'*len(placeholder)))
                Style.PROMPT.style('Input prompt for the image > '),
            )
            # TODO: to use image as prompt foe Vision api
            result = generate('llava', prompt, stream=False, images=[image_base64])
            self.poutput(Style.BOT.style(result['response']))

    doc_parser = cmd2.Cmd2ArgumentParser(description='Add documents for RAG')
    doc_parser.add_argument('path', help='Path of the document file or document folder', completer=cmd2.Cmd.path_complete)

    @cmd2.with_argparser(doc_parser)
    @cmd2.with_category(__app_name__)
    def do_add(self, args: argparse.Namespace):
        """Add documents for RAG"""
        # Load documents
        # TODO: Support other file types
        content = None
        type = filetype.guess(args.path)
        if type is None:
            if pathlib.Path(args.path).suffix.lower() == '.txt':
                with open(args.path, 'r') as f:
                    content = f.read()
        else:
            if type.mime == 'application/pdf':
                reader = PdfReader(args.path)
                pages = reader.pages
                for page in pages:
                    self.poutput(page.extract_text())
                
        # add to vector db
        if content is not None:
            self.embedor.add_doc(content)
            self.poutput(Style.INFO.style('Document added'))
    
    @cmd2.with_category(__app_name__)
    def do_clear(self, line):    
        """Clear screen and reset the chat session (history)"""    
        self.chatBot.reset()        
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
        self.poutput(Style.INFO.style('Chat session cleared'))

    @cmd2.with_category(__app_name__)
    def do_list(self, line):    
        """Show model list"""    
        self.chatBot.list()

    def default(self, statement):        
        # the argument will be passed here if app start with some arguments
        # TODO: need to ignore this!!!
        
        line = statement.raw
        if len(line) == 0:
            return
        
        self.chat(line)

    def chat(self, text):
        def chat_callback(stream):
            self.poutput(Style.BOT.style('{}'.format(stream)),end='')

        message =f"Using this data: {self.embedor.embedding(text)}. Respond to this prompt: {text}" if self.embedor.has_data() else text        
        say = self.chatBot.chat(message, chat_callback)
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
        
    def remove_commands(self):
        # TODO: This will cause error when change the model
        # del cmd2.Cmd.do_macro
        # del cmd2.Cmd.do_edit
        # del cmd2.Cmd.do_run_pyscript
        # del cmd2.Cmd.do_run_script
        pass

from __init__ import __app_name__, __version__
from app import App
import argparse

def main(env):
    import sys

    app = App(env)
    sys.exit(app.cmdloop())    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("env", help="Environment file", nargs="?", default=".openai.env")
    # parser.add_argument("model", help="Model name", nargs="?", default="gpt-3.5-turbo")
    # parser.add_argument("-t", "--tts", help="Enable TTS", action="store_true")
    parser.add_argument("-v", "--version", action="version", version=f"{__app_name__} v{__version__}")
    args = parser.parse_args()
    main(args.env)


# gtpshell

This is a simple chatbot shell application which is able to connect to any llama model. It supports speech recognition and text-to-speech.

![Architecture](architecture.png "Architecture")

## Dependencies

- Python 3.10 or higher
- OpenAI 

> pip install -r requirements.txt

## TTS (ChatTTS)

- Install

```bash
$ mkdir modules
$ cd modules
$ git submodule add https://github.com/2noise/ChatTTS.git
```

- Build

```bash
$ cd ChatTTS
$ pip install -r requirements.txt
```

## Distribution

Use PyInstaller to create a standalone executable.

> pip install pyinstaller

```python
$ pyinstaller -F gptshell/__main__.py
```

The standalone executable will be created in the dist folder.

TODO: Is it possible to distribute to mobile?

## TODO

- Save settings 
- Add image input
- Support such as Function Calling, RAG etc
- Develop a plugin system to support such as web search etc

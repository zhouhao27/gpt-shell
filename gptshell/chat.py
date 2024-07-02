from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import os
import ollama
from styles import Style
import cmd2
from cmd2 import (
    Fg,
    style,
)

class ChatBot(cmd2.Cmd): 
    def __init__(self, env_file, model_name=None):
        super().__init__(allow_cli_args=False)

        _ = load_dotenv(find_dotenv(env_file))

        # TODO: This might not be the best solution 
        self.is_openai = False
        if os.path.splitext(env_file)[0] == '.openai':
            self.is_openai = True
        
        self.client = OpenAI()
        if model_name is not None and model_name != '':
            self.model_name = model_name
        else:
            self.model_name = os.environ.get("DEFAULT_MODEL")
        self.reset()
    
    def chat(self,user_query, streaming_callback):
        
        self.history.append({"role": "user", "content": user_query})
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.history,
            temperature=0.5,
            # max_tokens=4096,
            stream=True
        )
        complete_response = ""
        for chunk in response:                
            if chunk.choices is not None:    
                if len(chunk.choices) > 0:            
                    if chunk.choices[0].delta.content is not None:
                        complete_response += chunk.choices[0].delta.content
                        streaming_callback(chunk.choices[0].delta.content)
        
        self.history.append({"role": "assistant", "content": complete_response})
        return complete_response
    
    def get_model_name(self):
        return self.model_name
    
    def reset(self):
        self.history = [
            {"role": "system", "content": "You are a helpful assistant."},
        ]

    def list(self):
        if self.is_openai:
            models = self.client.models.list()
            for model in models.data:
                if model.id == self.get_model_name():
                    self.poutput(Style.IMPORTANT.style(f"* {model.id}"))
                else:
                    self.poutput(Style.INFO.style(f"  {model.id}"))            
                    self.poutput(Style.INFO.style(f"Created: {model.created}"))
                    self.poutput(Style.INFO.style(f"Owned By: {model.owned_by}"))
                    self.poutput(Style.INFO.style("-" * 40))
        else:
            models = ollama.list()['models']
            for model in models:
                # How to know it's the current model?
                if model['name'] == self.get_model_name():
                    self.poutput(Style.IMPORTANT.style(f"* {model['name']}"))
                else:
                    self.poutput(Style.INFO.style(f"  {model['name']}"))            
                    self.poutput(Style.INFO.style(f"  family: {model['details']['family']}"))
                    self.poutput(Style.INFO.style(f"  parameter size: {model['details']['parameter_size']}"))
                    self.poutput(Style.INFO.style(f"  quantization level: {model['details']['quantization_level']}"))
                    self.poutput(Style.INFO.style("-" * 40))

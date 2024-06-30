from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import os

class ChatBot: 
    def __init__(self, env_file, model_name='gpt-3.5-turbo'):
        _ = load_dotenv(find_dotenv(env_file))

        self.client = OpenAI()
        self.model_name = os.environ.get("DEFAULT_MODEL")
        self.history = [
            {"role": "system", "content": "You are a helpful assistant."},
        ]
    
    def chat(self,user_query, streaming_callback):
        
        self.history.append({"role": "user", "content": user_query})
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.history,
            temperature=0.5,
            # max_tokens=4096,
            stream=True
        )
        for chunk in response:                
            if chunk.choices is not None:                
                if chunk.choices[0].delta.content is not None:
                    self.history.append(chunk.choices[0].delta)
                    streaming_callback(chunk.choices[0].delta.content)
        
    def get_model_name(self):
        return self.model_name


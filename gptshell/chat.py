from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import os

class ChatBot: 
    def __init__(self, env_file, model_name=None):
        _ = load_dotenv(find_dotenv(env_file))

        self.client = OpenAI()
        if model_name is not None:
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
                if chunk.choices[0].delta.content is not None:
                    # self.history.append({"role": "assistant", "content": chunk.choices[0].delta})
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
        return self.client.models.list()
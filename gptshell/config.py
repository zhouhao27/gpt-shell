import configparser

class Config:
    def __init__(self, env_file, config_file = 'config.conf'):        
        self.config = configparser.ConfigParser()
        self.config_file = config_file
        self.config.read(config_file)
        self.env = env_file

    def get_model(self) -> str:
        return self.__get(self.env, 'model')
        
    def set_model(self, model: str):
        self.__set(self.env, 'model', model)

    def get_tts(self) -> bool:
        return self.__get(self.env, 'tts')

    def set_tts(self, tts: bool):
        self.__set(self.env, 'tts', tts)

    def get_debug(self) -> bool:
        return self.__get(self.env, 'debug')
    
    def set_debug(self, debug: bool):
        self.__set(self.env, 'debug', debug)

    def __get(self, section, key):
        if not self.config.has_section(section):
            self.config.add_section(section)

        if not self.config.has_option(section, key):
            return None
        
        # TODO: need to implement default value? 
        return self.config[section][key]
    
    def __set(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)

        self.config.set(section, key, str(value))
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
        
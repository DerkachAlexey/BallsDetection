import json


class Config:

    def __init__(self, path_to_config='./data/config.json'):

        with open(path_to_config, 'r') as file:
            self.params = json.load(file)

    def get(self, key):

        return self.params[key]


import os
import shutil

class SensorGenerator:
    def __init__(self, juice_config):
        self.config = juice_config

    def generate_sensors(self, observation_dict, output_folder_path):
        # TODO: remove hardcoded sensors
        shutil.copytree(os.path.abspath(os.path.join(__file__,'..','sensors')),
                        os.path.abspath(os.path.join(output_folder_path,'sensors')))
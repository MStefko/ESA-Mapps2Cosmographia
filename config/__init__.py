import json
import os
import datetime
from collections import OrderedDict

import sys
if sys.version_info > (3,0):
    from configparser import ConfigParser
else:
    from ConfigParser import ConfigParser


class JuiceConfig(ConfigParser):

    def __init__(self, path):
        ConfigParser.__init__(self)
        self.file = os.path.join(path, 'juice_plugin.ini')
        self.read([self.file])
        self.set_property('runtime','last_use', str(datetime.datetime.utcnow()))

    def set_property(self, section, option, value):
        if not self.has_section(section) :
            self.add_section(section)
        self.set(section, option, value)
        self.save()

    def save(self):
        with open(self.file, 'w') as cfg:
            self.write(cfg)

    def get_property(self, section, option):
        if not self.has_option(section, option):
            return ""
        return self.get(section, option)

    def get_last_scenario_folder(self):
        return self.get_property('folders', 'scenario')

    def set_last_scenario_folder(self, value):
        self.set_property('folders', 'scenario', value)

    def get_last_attitude_folder(self):
        return self.get_property('folders', 'attitude')

    def set_last_attitude_folder(self, value):
        self.set_property('folders', 'attitude', value)

    def get_last_timeline_folder(self):
        return self.get_property('folders', 'timeline')

    def set_last_timeline_folder(self, value):
        self.set_property('folders', 'timeline', value)

    def get_last_evt_folder(self):
        return self.get_property('folders', 'evt')

    def set_last_evt_folder(self, value):
        self.set_property('folders', 'evt', value)

    def get_version(self):
        return self.get_property('runtime', 'version')

    def get_observation_lifetime(self):
        return int(self.get_property('ui', 'observation_lifetime_min'))

    def set_observation_lifetime_min(self, value_min):
        self.set_property('ui','observation_lifetime_min',str(int(value_min)))

    def get_object_property(self, section, option):
        if not self.has_option(section, option):
            return "{}"
        return self.get(section, option)

    def get_list_property(self, section, option):
        if not self.has_option(section, option):
            return "[]"
        return self.get(section, option)

    def get_checked_instruments(self):
        return self.get_property('ui','checked_instruments').split(',')

    def set_checked_instruments(self, instrument_list):
        self.set_property('ui','checked_instruments',",".join(instrument_list))

    def get_targets(self):
        return json.loads(self.get_list_property('itl','targets'))

    def get_selected_target(self):
        return self.get_property('ui', 'selected_target')

    def set_selected_target(self, selected_target):
        return self.set_property('ui', 'selected_target', selected_target)

    def get_mode_sensors(self):
        return json.loads(self.get_object_property('itl', 'mode_sensors'))

    def get_sensor_colors(self):
        return json.loads(self.get_object_property('itl', 'sensor_colors'))

    def get_instruments(self):
        return json.loads(self.get_list_property('itl', 'instruments'))

    def get_template_observation(self):
        template_path = os.path.abspath(os.path.join(__file__,'..','template_observation.json'))
        return json.load(open(template_path), object_pairs_hook=OrderedDict)

    def get_template_sensor(self):
        template_path = os.path.abspath(os.path.join(__file__,'..','template_sensor.json'))
        return json.load(open(template_path), object_pairs_hook=OrderedDict)
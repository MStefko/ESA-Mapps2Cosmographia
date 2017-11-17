import ConfigParser
import json
import os
import datetime
from collections import OrderedDict


class JuiceConfig(ConfigParser.ConfigParser):

    def __init__(self, path):
        ConfigParser.ConfigParser.__init__(self)
        self.file = os.path.join(path, 'juice_plugin.ini')
        self.read([self.file])
        self.set_property('runtime','last_use', datetime.datetime.utcnow())

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

    def get_mode_sensors(self):
        return json.loads(self.get_object_property('itl', 'mode_sensors'))

    def get_target(self):
        return self.get_property('itl', 'target')

    def get_events(self):
        return json.loads(self.get_object_property('itl', 'events'))

    def get_sensor_colors(self):
        return json.loads(self.get_object_property('ui', 'sensor_colors'))

    def get_instruments(self):
        return json.loads(self.get_list_property('itl', 'instruments'))

    def get_targets(self):
        return json.loads(self.get_list_property('ui', 'targets'))

    def get_template_observation(self):
        template_path = os.path.abspath(os.path.join(__file__,'..','template_observation.json'))
        return json.load(open(template_path), object_pairs_hook=OrderedDict)
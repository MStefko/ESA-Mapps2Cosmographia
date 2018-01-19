from __future__ import print_function
import json
import os
import datetime
from collections import OrderedDict, defaultdict

import sys
if sys.version_info > (3, 0):
    # noinspection PyCompatibility
    from configparser import ConfigParser
else:
    # noinspection PyCompatibility
    from ConfigParser import ConfigParser


class Config:
    class StaticConfig(ConfigParser):
        def __init__(self, path):
            ConfigParser.__init__(self)
            self.file = os.path.join(path, 'config_static.ini')
            self.read([self.file])

        def get_property(self, section, option):
            if not self.has_option(section, option):
                return ""
            return self.get(section, option)

        def get_object_property(self, section, option):
            if not self.has_option(section, option):
                return "{}"
            return self.get(section, option)

        def get_list_property(self, section, option):
            if not self.has_option(section, option):
                return "[]"
            return self.get(section, option)

        def get_template_sensor(self):
            template_path = os.path.abspath(os.path.join(__file__, '..', 'template_sensor.json'))
            return json.load(open(template_path), object_pairs_hook=OrderedDict)

        def get_template_observation(self):
            template_path = os.path.abspath(os.path.join(__file__, '..', 'template_observation.json'))
            return json.load(open(template_path), object_pairs_hook=OrderedDict)

        def get_mode_sensors(self):
            return json.loads(self.get_object_property('itl', 'mode_sensors'), object_pairs_hook=OrderedDict)

        def get_sensor_colors(self):
            # If entry is missing, the defaultdict will return a gray value
            def default_color():
                color = [0.5, 0.5, 0.5]
                return color

            return defaultdict(default_color, json.loads(self.get_object_property('itl', 'sensor_colors')))

        def get_instruments(self):
            return list(self.get_mode_sensors().keys())

        def get_targets(self):
            return json.loads(self.get_list_property('itl', 'targets'))

    class TempConfig(ConfigParser):
        def __init__(self, path):
            ConfigParser.__init__(self)
            self.file = os.path.join(path, 'config_temp.ini')
            self.read([self.file])
            self.set_property('runtime', 'last_use', str(datetime.datetime.utcnow()))

        def set_property(self, section, option, value):
            if not self.has_section(section):
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


    def __init__(self, path):
        self.static = Config.StaticConfig(path)
        self.temp = Config.TempConfig(path)

    def get_last_scenario_folder(self):
        return self.temp.get_property('folders', 'scenario')

    def set_last_scenario_folder(self, value):
        self.temp.set_property('folders', 'scenario', value)

    def get_last_attitude_folder(self):
        return self.temp.get_property('folders', 'attitude')

    def set_last_attitude_folder(self, value):
        self.temp.set_property('folders', 'attitude', value)

    def get_last_timeline_folder(self):
        return self.temp.get_property('folders', 'timeline')

    def set_last_timeline_folder(self, value):
        self.temp.set_property('folders', 'timeline', value)

    def get_last_evt_folder(self):
        return self.temp.get_property('folders', 'evt')

    def set_last_evt_folder(self, value):
        self.temp.set_property('folders', 'evt', value)

    def get_version(self):
        return self.static.get_property('runtime', 'version')

    def get_observation_lifetime(self):
        return int(self.temp.get_property('ui', 'observation_lifetime_min') or 0)

    def set_observation_lifetime_min(self, value_min):
        self.temp.set_property('ui', 'observation_lifetime_min', str(int(value_min)))

    def get_checked_instruments(self):
        return self.temp.get_property('ui', 'checked_instruments').split(',')

    def set_checked_instruments(self, instrument_list):
        self.temp.set_property('ui', 'checked_instruments', ",".join(instrument_list))

    def get_is_custom_start_time_enabled(self):
        return self.temp.getboolean('ui', 'is_custom_start_time_enabled')

    def set_is_custom_start_time_enabled(self, value):
        if not isinstance(value, bool):
            raise ValueError()
        self.temp.set('ui', 'is_custom_start_time_enabled', value)

    def get_custom_start_time(self):
        return self.temp.get_property('ui', 'custom_start_time')

    def set_custom_start_time(self, custom_start_time):
        self.temp.set_property('ui', 'custom_start_time', custom_start_time)

    def get_targets(self):
        return self.static.get_targets()

    def get_selected_target(self):
        return self.temp.get_property('ui', 'selected_target')

    def set_selected_target(self, selected_target):
        self.temp.set_property('ui', 'selected_target', selected_target)

    def get_template_sensor(self):
        return self.static.get_template_sensor()

    def get_template_observation(self):
        return self.static.get_template_observation()

    def get_mode_sensors(self):
        return self.static.get_mode_sensors()

    def get_sensor_colors(self):
        return self.static.get_sensor_colors()

    def get_instruments(self):
        return self.static.get_instruments()



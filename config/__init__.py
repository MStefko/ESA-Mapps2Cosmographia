import json
import os
import datetime
from collections import OrderedDict, defaultdict

from configparser import ConfigParser
from typing import Any, List


class Config:
    class StaticConfig(ConfigParser):
        def __init__(self, path: str):
            ConfigParser.__init__(self)
            self.file = os.path.join(path, 'config_static.ini')
            self.read([self.file])

        def get_property(self, section: str, option: str) -> str:
            if not self.has_option(section, option):
                return ""
            return self.get(section, option)

        def get_object_property(self, section: str, option: str) -> str:
            if not self.has_option(section, option):
                return "{}"
            return self.get(section, option)

        def get_list_property(self, section: str, option: str) -> str:
            if not self.has_option(section, option):
                return "[]"
            return self.get(section, option)

        @staticmethod
        def get_template_sensor() -> OrderedDict:
            template_path = os.path.abspath(os.path.join(__file__, '..', 'template_sensor.json'))
            return json.load(open(template_path), object_pairs_hook=OrderedDict)

        @staticmethod
        def get_template_observation() -> OrderedDict:
            template_path = os.path.abspath(os.path.join(__file__, '..', 'template_observation.json'))
            return json.load(open(template_path), object_pairs_hook=OrderedDict)

        def get_mode_sensors(self) -> OrderedDict:
            return json.loads(self.get_object_property('itl', 'mode_sensors'), object_pairs_hook=OrderedDict)

        def get_sensor_colors(self):
            # If entry is missing, the defaultdict will return a gray value
            def default_color():
                color = [0.5, 0.5, 0.5]
                return color

            return defaultdict(default_color, json.loads(self.get_object_property('itl', 'sensor_colors')))

        def get_instruments(self) -> List[str]:
            return list(self.get_mode_sensors().keys())

        def get_targets(self) -> List[str]:
            return json.loads(self.get_list_property('itl', 'targets'))

    class TempConfig(ConfigParser):
        def __init__(self, path: str):
            ConfigParser.__init__(self)
            self.file = os.path.join(path, 'config_temp.ini')
            self.read([self.file])
            self.set_property('runtime', 'last_use', str(datetime.datetime.utcnow()))

        def set_property(self, section: str, option: str, value: Any) -> None:
            if not self.has_section(section):
                self.add_section(section)
            self.set(section, option, value)
            self.save()

        def save(self) -> None:
            with open(self.file, 'w') as cfg:
                self.write(cfg)

        def get_property(self, section: str, option: str) -> str:
            if not self.has_option(section, option):
                return ""
            return self.get(section, option)

    def __init__(self, path: str):
        self.static = Config.StaticConfig(path)
        self.temp = Config.TempConfig(path)

    def get_last_scenario_folder(self) -> str:
        return self.temp.get_property('folders', 'scenario')

    def set_last_scenario_folder(self, value: str) -> None:
        self.temp.set_property('folders', 'scenario', value)

    def get_last_attitude_folder(self) -> str:
        return self.temp.get_property('folders', 'attitude')

    def set_last_attitude_folder(self, value: str) -> None:
        self.temp.set_property('folders', 'attitude', value)

    def get_last_timeline_folder(self) -> str:
        return self.temp.get_property('folders', 'timeline')

    def set_last_timeline_folder(self, value: str) -> None:
        self.temp.set_property('folders', 'timeline', value)

    def get_last_evt_folder(self) -> str:
        return self.temp.get_property('folders', 'evt')

    def set_last_evt_folder(self, value: str) -> None:
        self.temp.set_property('folders', 'evt', value)

    def get_version(self) -> str:
        return self.static.get_property('runtime', 'version')

    def get_observation_lifetime(self) -> int:
        return int(self.temp.get_property('ui', 'observation_lifetime_min') or 0)

    def set_observation_lifetime_min(self, value_min: Any) -> None:
        self.temp.set_property('ui', 'observation_lifetime_min', str(int(value_min)))

    def get_checked_instruments(self) -> List[str]:
        return self.temp.get_property('ui', 'checked_instruments').split(',')

    def set_checked_instruments(self, instrument_list: List[str]) -> None:
        self.temp.set_property('ui', 'checked_instruments', ",".join(instrument_list))

    def get_is_custom_start_time_enabled(self) -> bool:
        return self.temp.getboolean('ui', 'is_custom_start_time_enabled')

    def set_is_custom_start_time_enabled(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValueError()
        self.temp.set('ui', 'is_custom_start_time_enabled', str(value))

    def get_custom_start_time(self) -> str:
        return self.temp.get_property('ui', 'custom_start_time')

    def set_custom_start_time(self, custom_start_time: str) -> None:
        self.temp.set_property('ui', 'custom_start_time', custom_start_time)

    def get_targets(self) -> List[str]:
        return self.static.get_targets()

    def get_selected_target(self) -> str:
        return self.temp.get_property('ui', 'selected_target')

    def set_selected_target(self, selected_target: str) -> None:
        self.temp.set_property('ui', 'selected_target', selected_target)

    def get_template_sensor(self) -> OrderedDict:
        return self.static.get_template_sensor()

    def get_template_observation(self) -> OrderedDict:
        return self.static.get_template_observation()

    def get_mode_sensors(self) -> OrderedDict:
        return self.static.get_mode_sensors()

    def get_sensor_colors(self) -> defaultdict:
        return self.static.get_sensor_colors()

    def get_instruments(self) -> List[str]:
        return self.static.get_instruments()



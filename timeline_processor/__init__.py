from collections import namedtuple, OrderedDict
from datetime import datetime, timedelta
from config import JuiceConfig
import simplejson as json
import os

from timeline_processor.sensor_generator import SensorGenerator


class TimelineProcessor:
    def __init__(self, juice_config, instruments = None, observation_lifetime_s = 600):
        """

        :type juice_config: JuiceConfig
        """
        self.juice_config = juice_config
        self.parsed_timeline = None
        self.instruments = instruments if instruments else \
            self.juice_config.get_instruments()
        self.set_observation_lifetime_seconds(observation_lifetime_s)
        self.sensor_generator = SensorGenerator(juice_config)

    def process_scenario(self, timeline_file_path, require_json_path, output_folder_path):
        with open(timeline_file_path) as f:
            parsed_lines = self._parse_experiment_modes(f)
        observations = self._process_parsed_lines_into_observations(parsed_lines)
        self._generate_observation_files(observations, output_folder_path, require_json_path)
        self.sensor_generator.generate_sensors(observations, output_folder_path)

    def set_instruments(self, instrument_list):
        self.instruments = instrument_list

    def set_observation_lifetime_seconds(self, lifetime):
        if lifetime<0:
            raise ValueError("Negative observation lifetime.")
        self.observation_lifetime_seconds = lifetime

    def _parse_experiment_modes(self, f):
        # Find line that starts with "Experiment modes:", then skip 3 lines,
        # while checking that the third line is filled with ------
        for line in f:
            if line.startswith("Experiment modes:"):
                f.next(), f.next()
                if not f.next().startswith("-----"):
                    raise ValueError("Error in parsing file. Could not find start of Experiment modes section.")
                break
        # We are at beginning of our section
        parsed_lines = []
        Entry = namedtuple('Entry', ['utc_timestamp', 'instrument_name', 'mode'])
        for line in f:
            if len(line)<2: #one space for newline character
                break
            utc_timestamp = datetime.strptime(line[0:20], "%d-%b-%Y_%H:%M:%S")
            instrument_name = line[36:46].rstrip()
            mode = line[74:91].rstrip()
            parsed_lines.append( Entry(utc_timestamp, instrument_name, mode) )
        return parsed_lines

    def _process_parsed_lines_into_observations(self, parsed_lines):
        mode_sensors = self.juice_config.get_mode_sensors()
        observations = OrderedDict()
        for instrument in self.instruments:
            observations[instrument] = OrderedDict()
            entries = [e for e in parsed_lines if e.instrument_name == instrument]
            current_sensor = None
            for e in entries:
                if current_sensor is None:
                    if e.mode in mode_sensors:
                        start_time = e.utc_timestamp
                        current_sensor = mode_sensors[e.mode]
                    else:
                        continue
                else:
                    end_time = e.utc_timestamp
                    if current_sensor not in observations[instrument]:
                        observations[instrument][current_sensor] = []
                    observations[instrument][current_sensor].append( (start_time, end_time) )
                    if e.mode in mode_sensors:
                        current_sensor = mode_sensors[e.mode]
                        start_time = e.utc_timestamp
                    else:
                        current_sensor = None
            # if no sensor got entered for an instrument, delete the entry
            if not observations[instrument]:
                del observations[instrument]
        print observations
        return observations

    def _generate_observation_files(self, observations, output_folder_path, require_json_path):
        with open(require_json_path) as json_file:
            require_json = json.load(json_file)
        os.makedirs(os.path.abspath(os.path.join(output_folder_path,'observations')))
        for instrument_name, sensor_dict in observations.iteritems():
            for sensor_name, observation_list in sensor_dict.iteritems():
                # sensor JSON needs to be added first
                sensor_json_path = "sensors/sensor_{}_CALLISTO.json".format(sensor_name)
                if not sensor_json_path in require_json["require"]:
                    require_json["require"].append(sensor_json_path)
                for idx, times in enumerate(observation_list):
                    file_name = "JUICE_GEN_OBS_{}_{}.json".format(sensor_name, idx)
                    observation = self.juice_config.get_template_observation()
                    edit_entry = observation["items"][0]
                    edit_entry["name"] = file_name[:-5]
                    edit_entry["startTime"] = self._ftime(times[0])
                    edit_entry["endTime"] = self._ftime(self._delay_observation_end_time(times[1]))
                    d = OrderedDict()
                    d["startTime"] = self._ftime(times[0])
                    d["endTime"] = self._ftime(times[1])
                    d["obsRate"] = 0
                    edit_entry["geometry"]["groups"].append(d)
                    edit_entry["geometry"]["footprintColor"] = self.juice_config.get_sensor_colors()[instrument_name]
                    edit_entry["geometry"]["sensor"] = sensor_name
                    with open(os.path.abspath(os.path.join(output_folder_path,'observations',
                            file_name)), 'w+') as outfile:
                        json.dump(observation, outfile, indent=2)
                    # we need to add the observation file into the require json
                    require_json["require"].append("observations/{}".format(file_name))

        with open(require_json_path, 'w') as json_file:
            json.dump(require_json, json_file, indent=2)
        return

    def _ftime(self, time):
        return time.strftime("%Y-%m-%d %H:%M:%S.000 UTC")

    def _delay_observation_end_time(self, time):
        return time + timedelta(seconds=self.observation_lifetime_seconds)

if __name__=='__main__':
    print __file__
    config_path = os.path.abspath(os.path.join(__file__,'..','..'))

    config = JuiceConfig(config_path)

    print config.get_template_observation()
    p = TimelineProcessor(config)
    p.process_scenario(
        os.path.abspath(os.path.join(__file__,'..','test','example_timeline_data.asc')),
        os.path.abspath(os.path.join(__file__, '..', 'test', 'example_require.json')),
        os.path.abspath(os.path.join(__file__, '..', 'test', 'test_out'))
    )
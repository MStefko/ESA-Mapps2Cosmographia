from collections import namedtuple, OrderedDict
from datetime import datetime
from config import JuiceConfig
import simplejson as json
import os

class TimelineProcessor:
    def __init__(self, juice_config, instruments = None):
        """

        :type juice_config: JuiceConfig
        """
        self.juice_config = juice_config
        self.parsed_timeline = None
        self.instruments = instruments if instruments else \
            self.juice_config.get_boresights().keys()

    def process_scenario(self, timeline_file_path, require_json_path, output_folder_path):
        with open(timeline_file_path) as f:
            parsed_lines = self._parse_experiment_modes(f)
        observation_times = self._process_parsed_lines(parsed_lines)
        self._generate_observation_files(observation_times, output_folder_path, require_json_path)

    def set_instruments(self, instrument_list):
        self.instruments = instrument_list

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

    def _process_parsed_lines(self, parsed_lines):
        on_states = self.juice_config.get_on_states()
        print on_states
        observation_times = OrderedDict()
        for name in self.instruments:
            observation_times[name] = []
            entries = [e for e in parsed_lines if e.instrument_name==name]
            is_on = False
            for e in entries:
                if not is_on:
                    if e.mode in on_states:
                        start_time = e.utc_timestamp
                        is_on = True
                else:
                    if not e.mode in on_states:
                        end_time = e.utc_timestamp
                        observation_times[name].append( (start_time, end_time) )
                        is_on = False
        return observation_times

    def _generate_observation_files(self, observation_times, output_folder_path, require_json_path):
        with open(require_json_path) as json_file:
            require_json = json.load(json_file)

        for name, entries in observation_times.iteritems():
            file_name = "JUICE_GEN_OBS_{}.json".format(name)
            if not entries:
                continue
            observation = self.juice_config.get_template_observation()
            edit_entry = observation["items"][0]
            edit_entry["name"] = "JUICE_{}_OBS".format(name)
            edit_entry["startTime"] = self._ftime(entries[0][0])
            edit_entry["endTime"] = self._ftime(entries[-1][1])
            for entry in entries:
                d = OrderedDict()
                d["startTime"] = self._ftime(entry[0])
                d["endTime"] = self._ftime(entry[1])
                d["obsRate"] = 0
                edit_entry["geometry"]["groups"].append(d)
                edit_entry["geometry"]["footprintColor"] = self.juice_config.get_sensor_colors()[name]
                edit_entry["geometry"]["sensor"] = self.juice_config.get_boresights()[name]
            with open(os.path.abspath(os.path.join(output_folder_path,
                    file_name)), 'w+') as outfile:
                json.dump(observation, outfile, indent=2)

            # check if the required sensor JSON is included and if not, add it
            sensor_json_path = "../sensors/sensor_JUICE_{}_CALLISTO.json".format(name)
            if not sensor_json_path in require_json["require"]:
                require_json["require"].append(sensor_json_path)
            # now we need to add the observation file into the require json
            require_json["require"].append("../{}/{}".format(
                os.path.basename(os.path.abspath(output_folder_path)), file_name))


        with open(require_json_path, 'w') as json_file:
            json.dump(require_json, json_file, indent=2)


    def _ftime(self, time):
        return time.strftime("%Y-%m-%d %H:%M:%S.000 UTC")

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
import calendar
import traceback
from collections import namedtuple, OrderedDict
from datetime import datetime, timedelta
from typing import List

from attitude_converter.solar_panel_processor import SolarPanelProcessor
import spiceypy as spy

import sys

from config import Config
import simplejson as json
import os
import jdcal
import io

from timeline_processor.sensor_generator import SensorGenerator

Entry = namedtuple('Entry', ['utc_timestamp', 'instrument_name', 'mode'])


class TimelineProcessor:
    def __init__(self, juice_config: Config, instruments: list = None, observation_lifetime_s: int = 600):
        """

        :param instruments: List of instruments to parse, i.e. ["JANUS", "MAJIS"]
        :param observation_lifetime_s: Time after observation end for which the ground track
            is still shown.
        """
        self.juice_config = juice_config
        self.parsed_timeline = None
        self.instruments = instruments if instruments else \
            self.juice_config.get_instruments()
        self.set_observation_lifetime_seconds(observation_lifetime_s)
        self.sensor_generator = SensorGenerator(juice_config)

    def process_scenario(self, target_name: str, timeline_file_path: str, new_require_json_path: str,
                         custom_start_time: datetime = None, generate_solar_panels = False,
                         metakernel_file_path = None, ck_file_path = None) -> None:
        """ Parses scenario file from MAPPS timeline .asc file, and inserts the required
        sensors and observations into scenario JSON file.

        :param target_name: Name of target body (e.g. "Callisto")
        :param timeline_file_path: Path to MAPPS Timeline Dump .asc file. Can be an empty string
        :param new_require_json_path: Path to scenario JSON file in output folder.
        :param custom_start_time: (optional) Custom start time of scenario.
        """
        output_folder_path = os.path.abspath(os.path.dirname(new_require_json_path))
        if timeline_file_path:
            with open(timeline_file_path) as f:
                parsed_lines = self._parse_experiment_modes(f)
        else:
            parsed_lines = []
        observations = self._process_parsed_lines_into_observations(parsed_lines)
        self.sensor_generator.generate_sensors(observations, target_name, output_folder_path)
        self._generate_observation_files(observations, target_name, new_require_json_path)
        self._generate_bat_file(observations, new_require_json_path, target_name, custom_start_time)
        self._generate_bash_file(observations, new_require_json_path, target_name, custom_start_time)
        if generate_solar_panels:
            if metakernel_file_path is None or ck_file_path is None:
                raise ValueError("Specify both metakernel and ck file path!")
            self._generate_solar_panel_kernel(observations, metakernel_file_path, ck_file_path,
                                              output_folder_path, custom_start_time)

    def set_instruments(self, instrument_list: List[str]) -> None:
        """
        :param instrument_list: List of instruments to parse, i.e. ["JANUS", "MAJIS"]
        """
        self.instruments = instrument_list

    def set_observation_lifetime_seconds(self, lifetime: int) -> None:
        """
        :param lifetime: Time after observation end for which the ground track
            is still shown. [seconds]
        """
        if lifetime < 0:
            raise ValueError("Negative observation lifetime.")
        self.observation_lifetime_seconds = lifetime

    @staticmethod
    def _parse_experiment_modes(f: io.TextIOBase):
        """

        :param f: File handle of MAPPS Timeline Dump .asc file
        :return: List of parsed lines. Each entry is a namedtuple of format
            (utc_timestamp, instrument_name, mode).
        """
        parsed_lines = []
        # Find line that starts with "Experiment modes:", then skip 3 lines,
        # while checking that the third line is filled with ------
        for line in f:
            if line.startswith("Experiment modes:"):
                f.readline(), f.readline()
                if not f.readline().startswith("-----"):
                    raise ValueError("Error in parsing file. Could not find start of Experiment modes section.")
                # We are at beginning of our section
                for line in f:
                    # break at line that only has newline character
                    if len(line) < 3:
                        break
                    # parse the required entries on the line
                    utc_timestamp = datetime.strptime(line[0:20], "%d-%b-%Y_%H:%M:%S")
                    instrument_name = line[36:46].rstrip()
                    mode = line[74:91].rstrip()
                    parsed_lines.append(Entry(utc_timestamp, instrument_name, mode))
        return parsed_lines

    def _process_parsed_lines_into_observations(self, parsed_lines: List[Entry]) -> OrderedDict:
        """ Processes parsed lines into a nested dictionary, which for each instrument and
        each sensor contains a list of (start, end) times for individial observations.

        :param parsed_lines:  List of parsed lines. Each entry is a namedtuple of format
            (utc_timestamp, instrument_name, mode).
        :return: OrderedDict[instrument_name, OrderedDict[sensor_name, list[(start_time, end_time)]]]
        """
        mode_sensors = self.juice_config.get_mode_sensors()
        observations = OrderedDict()
        for instrument in self.instruments:
            observations[instrument] = OrderedDict()
            instrument_sensors = mode_sensors[instrument]
            relevant_entries = [e for e in parsed_lines if e.instrument_name == instrument]
            # Initially all sensors are assumed to be off
            current_sensor = None
            start_time = None
            for e in relevant_entries:
                if current_sensor is None:
                    # If the mode is in config_file, we turn it on
                    if e.mode in instrument_sensors:
                        start_time = e.utc_timestamp
                        current_sensor = instrument_sensors[e.mode]
                    else:
                        continue
                else:
                    # End current observation
                    end_time = e.utc_timestamp
                    # Check if current_sensor is already in dict, if not, create empty entry
                    if current_sensor not in observations[instrument]:
                        observations[instrument][current_sensor] = []
                    # Append observation to list for this sensor
                    observations[instrument][current_sensor].append((start_time, end_time))
                    # If next mode is in config file, we immediately start new observation
                    if e.mode in instrument_sensors:
                        current_sensor = instrument_sensors[e.mode]
                        start_time = e.utc_timestamp
                    # Otherwise, turn sensor off
                    else:
                        current_sensor = None
            # if no sensor got entered for an instrument, delete the entry
            if not observations[instrument]:
                del observations[instrument]
        return observations

    def _generate_observation_files(self, observations: OrderedDict, target_name: str,
                                    require_json_path: str) -> None:
        """ Generates and saves observation .json files from parsed observations.

        :param observations: OrderedDict[instrument_name, OrderedDict[sensor_name, list[(start_time, end_time)]]]
        :param target_name: Name of target body (e.g. "Callisto")
        :param require_json_path: Path to scenario file in output folder
        :return:
        """
        output_folder_path = os.path.abspath(os.path.dirname(require_json_path))
        with open(require_json_path) as json_file:
            require_json = json.load(json_file)

        os.makedirs(os.path.abspath(os.path.join(output_folder_path, 'observations')))

        # Iterate over each sensor
        for instrument_name, sensor_dict in observations.items():
            for sensor_name, observation_list in sensor_dict.items():
                # sensor JSON needs to be added to the require_json
                sensor_json_path = "sensors/sensor_{}_{}.json".format(sensor_name, target_name)
                if sensor_json_path not in require_json["require"]:
                    require_json["require"].append(sensor_json_path)
                # afterwards, we generate and add all individual observation .json files
                for idx, times in enumerate(observation_list):
                    file_name = "JUICE_GEN_OBS_{}_{}.json".format(sensor_name, idx)
                    observation = self.juice_config.get_template_observation()
                    edit_entry = observation["items"][0]
                    edit_entry["name"] = file_name[:-5]
                    edit_entry["startTime"] = self._ftime(times[0])
                    edit_entry["endTime"] = self._ftime(self._delay_observation_end_time(times[1]))
                    edit_entry["center"] = target_name
                    edit_entry["trajectoryFrame"]["body"] = target_name
                    edit_entry["bodyFrame"]["body"] = target_name
                    d = OrderedDict()
                    d["startTime"] = self._ftime(times[0])
                    d["endTime"] = self._ftime(times[1])
                    d["obsRate"] = 0
                    edit_entry["geometry"]["groups"].append(d)
                    edit_entry["geometry"]["footprintColor"] = self.juice_config.get_sensor_colors()[instrument_name]
                    edit_entry["geometry"]["sensor"] = sensor_name
                    with open(os.path.abspath(os.path.join(output_folder_path, 'observations',
                                                           file_name)), 'w+') as outfile:
                        json.dump(observation, outfile, indent=2)
                    # add corresponding entry to require_json
                    require_json["require"].append("observations/{}".format(file_name))
        # save updated require_json
        with open(require_json_path, 'w') as json_file:
            json.dump(require_json, json_file, indent=2)
        return

    def _generate_solar_panel_kernel(self, observations, metakernel_file_path, ck_file_path,
                                     output_folder_path, custom_start_time,
                                     extra_time_hours: float = 24, step_size_s: float = 20):
        spp = SolarPanelProcessor("JUICE")
        spy.furnsh(metakernel_file_path)
        spy.furnsh(ck_file_path)

        td = timedelta(hours=extra_time_hours)
        if custom_start_time is not None and len(observations)==0:
            start_time = custom_start_time + td
            end_time = custom_start_time - td
        else:
            start_time = self._find_first_start_time(observations) - td
            end_time = self._find_last_end_time(observations) + td

        spp.create_panel_ck(start_time, end_time, step_size_s,
                            os.path.abspath(os.path.join(output_folder_path, 'spacecraft', 'solar_panel_kernel.ck')))
        spy.unload(ck_file_path)
        spy.unload(metakernel_file_path)

        spacecraft_json_path = os.path.join(output_folder_path, "spacecraft", "spacecraft", "JUICE_panel_def.json")
        with open(spacecraft_json_path) as f:
            spacecraft_json = json.load(f)
        during = spacecraft_json["items"][0]
        before = spacecraft_json["items"][1]
        after = spacecraft_json["items"][2]

        def format_time_str(time: datetime) -> str:
            return time.strftime("%Y-%m-%d %H:%M:%S.000 UTC")
        during["startTime"] = format_time_str(start_time)
        during["endTime"] = format_time_str(end_time)
        before["endTime"] = format_time_str(start_time)
        after["startTime"] = format_time_str(end_time)

        with open(spacecraft_json_path, 'w') as json_file:
            json.dump(spacecraft_json, json_file, indent=2)
        return


    def _generate_bat_file(self, observations: OrderedDict, require_json_path: str,
                           target_name: str, start_time_override: datetime = None) -> None:
        """ Generates .bat file (Windows) that can launch Cosmographia already with the scenario loaded
        with camera following JUICE, and at time of beginning of first parsed obsevation,
        or at defined start time.

        Note: Start time is moved back by 20 minutes due to Cosmographia's fade-in startup.

        :param observations: Observation dictionary, used to determine start time
        :param require_json_path: Path to observation base .json file
        :param target_name: name of target to track at start
        :param start_time_override: (optional) Custom starting time of bat file
        :return:
        """
        bat_file_name = "run_scenario.bat"
        dt = start_time_override if start_time_override is not None else self._find_first_start_time(observations)
        # subtract 20 minutes
        td = timedelta(minutes=20)
        start_time_jd = self._get_jd_time(dt - td)
        output_dir_path = os.path.abspath(os.path.dirname(require_json_path))
        output_dir_short_path = os.path.join("JUICE", os.path.basename(output_dir_path))
        output_bat_file_path = os.path.abspath(os.path.join(output_dir_path, bat_file_name))
        with open(output_bat_file_path, 'w+') as f:
            # the string specifies the location and camera orientation next to JUICE, you can get a similar
            # string URL by pressing Ctrl+U in Cosmographia
            # frame=bfix (means body fixed frame around selected target)
            # jd: start time in mean julian days
            # x,y,z,qw,qx,qy,qz: position and orientation of camera, easiest to get using Ctrl+U
            # ts: time step, it is speed of time in Cosmographia when it starts
            # fov: width of field of view in degrees, 50 is a good number
            file_contents = \
f'''REM Generated on platform: {sys.platform}

Cosmographia "%cd%\{os.path.basename(require_json_path)}" -u "cosmo:JUICE?select=JUICE&frame=track&ftarget={target_name}&jd={start_time_jd:.5f}&x=1.893473&y=0.961017&z=4.926394&qw=-0.992279&qx=0.070385&qy=-0.097857&qz=-0.029180&ts=200&fov=50"

'''
            f.write(file_contents)
        return

    def _generate_bash_file(self, observations: OrderedDict, require_json_path: str,
                            target_name: str, start_time_override: datetime = None) -> None:
        """ Generates bash file (Mac/Linux) that can launch Cosmographia already with the scenario loaded
        with camera following JUICE, and at time of beginning of first parsed obsevation,
        or at defined start time.

        Note: Start time is moved back by 20 minutes due to Cosmographia's fade-in startup.

        :param observations: Observation dictionary, used to determine start time
        :param require_json_path: Path to observation base .json file
        :param target_name: name of target to track at start
        :param start_time_override: (optional) Custom starting time of sh file
        :return:
        """
        sh_file_name = "run_scenario.sh"
        dt = start_time_override if start_time_override is not None else self._find_first_start_time(observations)
        # subtract 20 minutes
        td = timedelta(minutes=20)
        start_time_jd = self._get_jd_time(dt - td)
        output_dir_path = os.path.abspath(os.path.dirname(require_json_path))
        output_dir_short_path = os.path.join("JUICE", os.path.basename(output_dir_path))
        output_sh_file_path = os.path.abspath(os.path.join(output_dir_path, sh_file_name))

        with open(output_sh_file_path, 'w+') as f:
            # the string specifies the location and camera orientation next to JUICE, you can get a similar
            # string URL by pressing Ctrl+U in Cosmographia
            # frame=bfix (means body fixed frame around selected target)
            # jd: start time in mean julian days
            # x,y,z,qw,qx,qy,qz: position and orientation of camera, easiest to get using Ctrl+U
            # ts: time step, it is speed of time in Cosmographia when it starts
            # fov: width of field of view in degrees, 50 is a good number
            file_contents = \
f'''#!/bin/bash
# Generated on platform: {sys.platform}

DIR="$( cd "$( dirname "$0" )" && pwd )"

Cosmographia "${{DIR}}/{os.path.basename(require_json_path)}" -u "cosmo:JUICE?select=JUICE&frame=track&ftarget={target_name}&jd={start_time_jd:.5f}&x=1.893473&y=0.961017&z=4.926394&qw=-0.992279&qx=0.070385&qy=-0.097857&qz=-0.029180&ts=200&fov=50"

'''
            f.write(file_contents)
        return

    @staticmethod
    def _get_jd_time(timestamp: datetime) -> float:
        """ Calculate MJD time from a timestamp.

        :param timestamp: Time to convert
        :return: Calculated mjd time.
        """
        jd_midnight = sum(jdcal.gcal2jd(timestamp.year, timestamp.month, timestamp.day))
        jd = sum([jd_midnight, timestamp.hour / 24.0, timestamp.minute / (24.0 * 60),
                  timestamp.second / (24.0 * 60 * 60)])
        return jd

    @staticmethod
    def _find_first_start_time(observations: OrderedDict) -> datetime:
        """ Finds the earliest start time of an observation.

        :param observations: Observation dictionary
        :return:
        """
        times = []
        for instrument_name, sensor_dict in observations.items():
            for sensor_name, observation_list in sensor_dict.items():
                for observation in observation_list:
                    times.append(observation[0])
        try:
            return min(times, key=lambda s: calendar.timegm(s.utctimetuple()))
        except ValueError:
            traceback.print_exc()
            return datetime.now()

    @staticmethod
    def _find_last_end_time(observations: OrderedDict) -> datetime:
        """ Finds the latest end time of an observation.

        :param observations: Observation dictionary
        :return:
        """
        times = []
        for instrument_name, sensor_dict in observations.items():
            for sensor_name, observation_list in sensor_dict.items():
                for observation in observation_list:
                    times.append(observation[1])
        try:
            return max(times, key=lambda s: calendar.timegm(s.utctimetuple()))
        except ValueError:
            traceback.print_exc()
            return datetime.now()

    @staticmethod
    def _ftime(time: datetime) -> str:
        """ Formats timestamp into a Cosmographia-compatible format.

        :param time: Timestamp to be formatted
        :return: Time string correctly formatted for Cosmographia JSON files
        """
        return time.strftime("%Y-%m-%d %H:%M:%S.000 UTC")

    def _delay_observation_end_time(self, time: datetime) -> datetime:
        """ Delays the timestamp by amount defined by self.observation_lifetime_seconds.

        :param time: Timestamp to be delayed
        :return: Delayed timestamp
        """
        return time + timedelta(seconds=self.observation_lifetime_seconds)

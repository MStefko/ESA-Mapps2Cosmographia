import os
import simplejson as json
from collections import OrderedDict


class ScenarioProcessor:
    def __init__(self, juice_config):
        self.juice_config = juice_config

    def process_scenario(self, scenario_file_path, output_folder_name, ck_file_name):
        # type: (str, str, str) -> str
        """ Loads already existing Cosmographia scenario file, inserts the new CK kernel,
        all necessary sensor and observation files, and saves the scenario to output
        folder.

        :param scenario_file_path: Original Cosmographia scenario file path.
        :param output_folder_name: Path to created output folder of this script.
        :param ck_file_name: Name of generated CK file.
        :return: Path to generated scenario JSON path.
        """
        root_folder = os.path.abspath(os.path.join(scenario_file_path, '..', '..'))

        with open(scenario_file_path) as f:
            self.scenario = json.load(f, object_pairs_hook=OrderedDict)
        # this root scenario file can but doesn't have to contain the "spiceKernels" entry
        if not "spiceKernels" in self.scenario:
            # We need to look for "spiceKernels" entry in the other .json files.
            # This file should have a field "require" which contains a path to .json file
            # which will hopefully the field "spiceKernels"
            if not "require" in self.scenario:
                raise ValueError('Neither "require" nor "spiceKernels" fields present in .json file.')
            kernel_file_path = None
            kernel_file_id = None
            # Iterate over the files, and look for the file that contains "spiceKernels"
            for idx, file_relative_path in enumerate(self.scenario["require"]):
                file_path = os.path.abspath(
                    os.path.join(scenario_file_path, '..', *tuple(file_relative_path.split('/'))))
                with open(file_path) as f:
                    try:
                        kernel_json = json.load(f, object_pairs_hook=OrderedDict)
                    except ValueError:
                        continue
                if "spiceKernels" in kernel_json:
                    # Found it! Keep track of what is the position in "require" field as well.
                    kernel_file_path = file_relative_path
                    kernel_file_id = idx
                    break
            if kernel_file_path is None:
                raise RuntimeError('Could not find JSON file containing "spiceKernels".')

            # Now we know which file contains the "spiceKernels" entry
            # We add our own kernel to the list
            kernel_json["spiceKernels"].append("../{}/{}".format(output_folder_name, ck_file_name))
            # save the new json file into our folder
            with open(os.path.abspath(os.path.join(root_folder,output_folder_name,
                                   os.path.basename(kernel_file_path))), 'w+') as outfile:
                json.dump(kernel_json, outfile, indent=2)

            # replace the entry in the original scenario file with our own spiceKernels JSON
            self.scenario["require"][kernel_file_id] = "../{}/{}".format(output_folder_name,
                                   os.path.basename(kernel_file_path))

            new_scenario_name = "LOAD_SCENARIO.json"
            # check if we would have a name conflict with kernel file
            # (i.e. kernel file is named "LOAD_SCENARIO.json" as well).
            # if we do, change the scenario file name to "RUN_SCENARIO.json"
            if os.path.basename(kernel_file_path)==new_scenario_name:
                new_scenario_name = "RUN_SCENARIO.json"

            new_scenario_file_path = os.path.abspath(os.path.join(root_folder,
                output_folder_name, new_scenario_name))
            # write the scenario JSON file
            with open(new_scenario_file_path, 'w+') as outfile:
                json.dump(self.scenario, outfile, indent=2)
        return new_scenario_file_path


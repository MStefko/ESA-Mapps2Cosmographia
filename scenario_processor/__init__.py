import os
import simplejson as json
from collections import OrderedDict


class ScenarioProcessor:
    def __init__(self, juice_config):
        self.juice_config = juice_config

    def process_scenario(self, scenario_file_path, output_folder_name, ck_file_name):
        root_folder = os.path.abspath(os.path.join(scenario_file_path, '..', '..'))
        print root_folder

        with open(scenario_file_path) as f:
            self.scenario = json.load(f, object_pairs_hook=OrderedDict)

        if not "spiceKernels" in self.scenario:
            # It should have a field "require" which contains a path to .json file which contains
            # the field "spiceKernels"
            if not "require" in self.scenario:
                raise ValueError('Neither "require" nor "spiceKernels" fields present in .json file.')
            kernel_file_path = None
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
                    kernel_file_path = file_relative_path
                    kernel_file_id = idx
                    break
            if kernel_file_path is None:
                raise RuntimeError('Could not find JSON file containing "spiceKernels".')
            # Now we know which file contains the "spiceKernels" entry
            # We add our own kernel to the list
            kernel_json["spiceKernels"].append("../{}/{}".format(output_folder_name, ck_file_name))
            # save the new json file into out folder
            with open(os.path.abspath(os.path.join(root_folder,output_folder_name,
                                   os.path.basename(kernel_file_path))), 'w+') as outfile:
                json.dump(kernel_json, outfile, indent=2)
            print kernel_json

            # replace the entry in the original scenario file
            self.scenario["require"][kernel_file_id] = "../{}/{}".format(output_folder_name,
                                   os.path.basename(kernel_file_path))

            # check if we would have a name conflict
            if os.path.basename(kernel_file_path)==os.path.basename(scenario_file_path):
                # if we do, append _SCENARIO at the end of scenario file
                new_scenario_name = os.path.basename(kernel_file_path)[:-5] + "_SCENARIO.json"
            else:
                new_scenario_name = os.path.basename(kernel_file_path)
            new_scenario_file_path = os.path.abspath(os.path.join(root_folder,output_folder_name,
                                   new_scenario_name))
            # write this file as well
            with open(new_scenario_file_path, 'w+') as outfile:
                json.dump(self.scenario, outfile, indent=2)
            print kernel_json
        return new_scenario_file_path


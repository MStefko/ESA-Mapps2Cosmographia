import os
from scenario_processor import ScenarioProcessor

if __name__=='__main__':
    scenario_path = os.path.abspath("test\\scenarios\\juice_crema_3_2_v151.json")
    s = ScenarioProcessor(None)
    s.process_scenario(scenario_path, "mapps_output_001", "kernel.ck")
    print s.scenario
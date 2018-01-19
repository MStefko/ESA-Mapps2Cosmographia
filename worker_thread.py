import os
import traceback
import time
from typing import Tuple, TYPE_CHECKING
# workaround to make type checking work with circular imports
if TYPE_CHECKING:
    from ui.gui_widget import MappsConverter

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread

from ui.working import Ui_Dialog

def generation_task(gui: 'MappsConverter') -> Tuple[int, str, str]:
    """ Generates the scenario from inputs.
    First, parse all file names. Then, use MEX2KER to convert MAPPS attitude into
    a CK kernel. Generate a scenario using the MAPPS timeline, and put all necessary
    include files into the folder.

    :param gui: Instance of main GUI
    :return: Return 3-tuple in format (exit_code, message, scenario_file_path)
    """
    try:
        gui.parse_instrument_checkboxes()
        target_name = gui.form.comboBox_targetList.currentText()
        gui.juice_config.set_selected_target(target_name)

        obs_lifetime_min = int(gui.form.le_ObsDecayTimeMin.text())
        if obs_lifetime_min < 0:
            raise ValueError("Observation decay time can't be negative.")
        gui.timeline_processor.set_observation_lifetime_seconds(60 * obs_lifetime_min)
        gui.juice_config.set_observation_lifetime_min(obs_lifetime_min)

        ck_file_name = 'mapps_attitude_kernel.ck'
        attitude_file = gui.form.le_MappsAttitude.text()
        scenario_file = gui.form.le_Scenario.text()
        timeline_file = gui.form.le_MappsTimeline.text()

        scenario_folder = os.path.dirname(scenario_file)
        new_folder_name = 'mapps_output_' + time.strftime("%Y%m%d_%H%M%S")
        new_folder_path = os.path.abspath(os.path.join(scenario_folder, '..', new_folder_name))
        print("Creating scenario directory: {}".format(new_folder_path))
        os.makedirs(new_folder_path)

        output_ck_path = os.path.abspath(os.path.join(new_folder_path, ck_file_name))
        print("Generating CK kernel: {}".format(output_ck_path))
        gui.attitude_converter.convert(attitude_file, output_ck_path)

        new_scenario_file_path = gui.scenario_processor.process_scenario(
            scenario_file, new_folder_name, ck_file_name)
        print("Generating scenario file: {}".format(new_scenario_file_path))
        gui.timeline_processor.process_scenario(target_name, timeline_file,
                                                new_scenario_file_path, gui.parse_custom_start_time())
        print("Finished.")
    except Exception as e:
        msg = (1, traceback.format_exc(0) + "\nSee console for more details.", "")
        traceback.print_exc()
    else:
        msg = (0, 'Scenario file generated at:\n\n{}'.format(new_scenario_file_path), new_scenario_file_path)
    return msg


class TaskRunner(QThread):
    """
    Thread that actually executes the generation_task
    """
    def __init__(self, gui: 'MappsConverter'):
        super(TaskRunner, self).__init__()
        self.gui = gui

    def run(self):
        """Execute the generation_task, and dump the exit message back to
        the gui."""
        msg = generation_task(self.gui)
        self.dump_msg(msg)

    def dump_msg(self, msg: Tuple[int, str, str]):
        self.gui.set_exit_message(msg)


class WorkingMessage(QtWidgets.QDialog):
    def __init__(self, msg: str = 'Working ', parent = None):
        super(WorkingMessage, self).__init__(parent)
        self.dialog = Ui_Dialog()
        self.dialog.setupUi(self)

        # Initialize Values
        self.o_msg = msg
        self.msg = msg
        self.val = 0

        self.dialog.info_label.setText(msg)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_message)
        self.timer.start()

    def update_message(self):
        self.val += 1
        self.msg += '.'

        if self.val < 20:
            self.dialog.info_label.setText(self.msg)
        else:
            self.val = 0
            self.msg = self.o_msg

    def loading_stop(self):
        self.timer.stop()
        self.destroy()

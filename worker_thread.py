import os
import traceback
import time

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread

from ui.working import Ui_Dialog
from attitude_converter import convert

from typing import Tuple, TYPE_CHECKING
# workaround to make type checking work with circular imports
if TYPE_CHECKING:
    from ui.gui_widget import MappsConverter


def generation_task(gui: 'MappsConverter', display_function = None) -> Tuple[int, str, str]:
    """ Generates the scenario from inputs.
    First, parse all file names. Then, use MEX2KER to convert MAPPS attitude into
    a CK kernel. Generate a scenario using the MAPPS timeline, and put all necessary
    include files into the folder.

    :param gui: Instance of main GUI
    :return: Return 3-tuple in format (exit_code, message, scenario_file_path)
    """
    def display_status(message):
        print(message)
        try:
            display_function(message)
        except Exception:
            pass

    try:
        display_status("Parsing GUI values.")
        gui.parse_instrument_checkboxes()
        target_name = gui.form.comboBox_targetList.currentText()
        gui.juice_config.set_selected_target(target_name)

        apply_solar_panels = gui.form.cb_solarPanels.isChecked()
        gui.juice_config.set_is_solar_panel_rotation_enabled(apply_solar_panels)

        obs_lifetime_min = int(gui.form.le_ObsDecayTimeMin.text())
        if obs_lifetime_min < 0:
            raise ValueError("Observation decay time can't be negative.")
        gui.timeline_processor.set_observation_lifetime_seconds(60 * obs_lifetime_min)
        gui.juice_config.set_observation_lifetime_min(obs_lifetime_min)

        ck_file_name = 'mapps_attitude_kernel.ck'
        attitude_file = gui.form.le_MappsAttitude.text()
        metakernel_file = gui.form.le_Metakernel.text()
        timeline_file = gui.form.le_MappsTimeline.text()
        output_folder_path = gui.form.le_OutputFolderPath.text()
        output_folder_name = gui.form.le_OutputFolderName.text()
        gui.juice_config.set_last_output_folder(output_folder_name)

        real_folder_path = create_output_folder(os.path.join(output_folder_path, output_folder_name))
        print("Created scenario directory: {}".format(real_folder_path))

        display_status("Generating CK kernel.")
        output_ck_path = os.path.abspath(os.path.join(real_folder_path, ck_file_name))
        print("Generating CK kernel: {}".format(output_ck_path))
        convert(attitude_file, output_ck_path)

        display_status("Generating scenario file.")
        if apply_solar_panels:
            display_status("Generating solar panel kernel.")
        new_scenario_file_path = gui.scenario_processor.process_scenario(
            metakernel_file, real_folder_path, ck_file_name, apply_solar_panels)
        print("Generating scenario file: {}".format(new_scenario_file_path))
        gui.timeline_processor.process_scenario(target_name, timeline_file,
                                                new_scenario_file_path, gui.parse_custom_start_time(),
                                                apply_solar_panels, metakernel_file,
                                                os.path.abspath(os.path.join(real_folder_path, ck_file_name)))
        print("Finished.")
    except Exception as e:
        msg = (1, traceback.format_exc(0) + "\nSee console for more details.", "")
        traceback.print_exc()
    else:
        msg = (0, 'Scenario file generated at:\n\n{}'.format(new_scenario_file_path), new_scenario_file_path)
    return msg


def create_output_folder(output_folder_path: str) -> str:
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
        return output_folder_path
    else:
        for i in range(1000):
            new_path = os.path.join(os.path.dirname(output_folder_path),os.path.basename(output_folder_path) + f"_{i:03d}")
            if not os.path.exists(new_path):
                os.makedirs(new_path)
                return new_path
        raise RuntimeError(f"Could not create folder {output_folder_path}")

class TaskRunner(QThread):
    """
    Thread that actually executes the generation_task
    """
    def __init__(self, gui: 'MappsConverter'):
        super(TaskRunner, self).__init__()
        self.gui = gui
        self._message_function = None

    def run(self):
        """Execute the generation_task, and dump the exit message back to
        the gui."""
        msg = generation_task(self.gui, self._message_function)
        self.dump_msg(msg)

    def set_message_function(self, message_function):
        self._message_function = message_function

    def dump_msg(self, msg: Tuple[int, str, str]):
        self.gui.set_exit_message(msg)


class WorkingMessage(QtWidgets.QDialog):
    def __init__(self, msg: str = 'Working ', parent: QtWidgets.QDialog = None):
        super(WorkingMessage, self).__init__(parent)
        self.dialog = Ui_Dialog()
        self.dialog.setupUi(self)

        # Initialize Values
        self.o_msg = msg
        self.val = 0

        self.dialog.info_label.setText(msg)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(250)
        self.timer.timeout.connect(self.update_message)
        self.timer.start()

    def set_message(self, status: str):
        self.o_msg = status
        self.update_message()

    def update_message(self):
        if self.val < 3:
            self.val += 1
        else:
            self.val = 0

        msg = self.o_msg + "." * self.val
        self.dialog.info_label.setText(msg)

    def loading_stop(self):
        self.timer.stop()
        self.destroy()

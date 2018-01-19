from __future__ import print_function
import os
import sys
import traceback
from datetime import datetime
from collections import OrderedDict
from typing import Tuple, Union

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from config import Config
from worker_thread import TaskRunner, WorkingMessage
from ui.juice_win_converter import Ui_Form
from scenario_processor import ScenarioProcessor
from timeline_processor import TimelineProcessor


class MappsConverter(QWidget):

    def __init__(self, parent: QWidget, juice_config: Config):
        """

        :param parent: Parent widget
        :param juice_config: Config file
        """
        super(MappsConverter, self).__init__(parent)
        self.exit_message = (0, "No exit message.")
        self.execute_bat_script = False
        self.juice_config = juice_config
        self.scenario_processor = ScenarioProcessor(juice_config)
        self.timeline_processor = TimelineProcessor(juice_config)

        self.form = Ui_Form()
        self.form.setupUi(self)
        # insert text values to form
        self.form.l_version.setText(juice_config.get_version())
        self.form.le_MappsAttitude.setText(self.juice_config.get_last_attitude_folder())
        self.form.le_MappsTimeline.setText(self.juice_config.get_last_timeline_folder())
        self.form.le_Scenario.setText(self.juice_config.get_last_scenario_folder())
        self.form.le_ObsDecayTimeMin.setText(str(self.juice_config.get_observation_lifetime()))

        # populate target combobox
        self.form.comboBox_targetList.clear()
        self.form.comboBox_targetList.addItems(self.juice_config.get_targets())
        # select last selected item in combobox
        text = self.juice_config.get_selected_target()
        index = self.form.comboBox_targetList.findText(text, Qt.MatchFixedString)
        if index >= 0:
            self.form.comboBox_targetList.setCurrentIndex(index)

        self._populate_instrument_table()
        self._configure_start_time_entry()
        self.setMaximumSize(self.size())
        self.setMinimumSize(self.size())
        self.show()

    def _populate_instrument_table(self) -> None:
        # load values from config
        instrument_list = self.juice_config.get_instruments()
        checked_instruments = self.juice_config.get_checked_instruments()

        table = self.form.instrumentTable
        table.setRowCount(len(instrument_list))

        # insert into table and keep track of inserted checkboxes
        self.instrument_checkboxes = OrderedDict()
        for idx, name in enumerate(instrument_list):
            item = QTableWidgetItem(name)
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            if name in checked_instruments:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            # insert in 0-th column
            table.setItem(idx, 0, item)
            self.instrument_checkboxes[name] = item

    def _configure_start_time_entry(self) -> None:
        # load values from config
        is_start_time_enabled = self.juice_config.get_is_custom_start_time_enabled()
        start_time = self.juice_config.get_custom_start_time()

        self.form.le_StartTime.setText(start_time)
        if is_start_time_enabled:
            self.form.cb_startTime.setChecked(True)
            self.form.le_StartTime.setEnabled(True)

    def parse_instrument_checkboxes(self) -> None:
        """ Retrieves check values from GUI and informs the timeline processor and config. """
        checked_instruments = []
        for name, item in self.instrument_checkboxes.items():
            if item.checkState() == Qt.Checked:
                checked_instruments.append(name)
        self.juice_config.set_checked_instruments(checked_instruments)
        self.timeline_processor.set_instruments(checked_instruments)

    def start_time_cb_changed(self, _: int) -> None:
        state = self.form.cb_startTime.isChecked()
        self.form.le_StartTime.setEnabled(state)
        self.juice_config.set_is_custom_start_time_enabled(state)

    def browse_attitude(self) -> None:
        last_selection = os.path.dirname(self.juice_config.get_last_attitude_folder())
        f = QFileDialog.getOpenFileName(self, "Open Mapps Data File", last_selection, "CSV data files (*.csv)")
        if f:
            file_name = str(f[0])
            self.juice_config.set_last_attitude_folder(file_name)
            self.form.le_MappsAttitude.setText(file_name)
             
    def browse_timeline(self) -> None:
        last_selection = os.path.dirname(self.juice_config.get_last_timeline_folder())
        f = QFileDialog.getOpenFileName(self, "Open Mapps Timeline File", last_selection,
                                        "MAPPS timeline files (*.asc *.txt)")
        if f:
            file_name = str(f[0])
            self.juice_config.set_last_timeline_folder(file_name)
            self.form.le_MappsTimeline.setText(file_name)
             
    def browse_scenario(self) -> None:
        last_selection = os.path.dirname(self.juice_config.get_last_scenario_folder())
        f = QFileDialog.getOpenFileName(self, "Open Cosmographia Scenario File", last_selection,
                                        "Cosmographia scenario files (*.json)")
        if f:
            file_name = str(f[0])
            self.juice_config.set_last_scenario_folder(file_name)
            self.form.le_Scenario.setText(file_name)

    def generate(self) -> None:
        """ Create the Working... mesage window, connect required thread signals together
        and start the TaskRunner thread.
        """
        # verify all three files exist
        try:
            self._verify_file_existence()
            self.parse_custom_start_time()
        except Exception as e:
            QMessageBox.warning(
                self, "File missing!", traceback.format_exc(0),
                QMessageBox.Ok, QMessageBox.Ok)
            traceback.print_exc()
            return

        # verify scenario file is placed in good location for bat script
        self.execute_bat_script = True
        scenario_error_message = self._verify_scenario_file_location()
        # if we have an error, display error message
        if scenario_error_message[0]:
            response = QMessageBox.warning(
                self, "Scenario file location warning",
                scenario_error_message[1], QMessageBox.Ok | QMessageBox.Abort,
                QMessageBox.Ok)
            # also disable generation of bat file because it wouldn't work
            self.execute_bat_script = False
            if response == QMessageBox.Abort:
                return

        # run the generation task
        self.task_runner = TaskRunner(self)
        self.busy_widget = WorkingMessage("Working")
        self.task_runner.finished.connect(self.loading_stop)
        self.task_runner.start()
        self.busy_widget.show()

    def parse_custom_start_time(self) -> Union[datetime, None]:
        if not self.form.cb_startTime.isChecked():
            return None
        start_time_string = self.form.le_StartTime.text()
        try:
            dt = datetime.strptime(start_time_string, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            raise ValueError("Error while parsing custom start time. Entry should have format '%YYYY-%MM-%DDT%hh:%mm:%ss'.")
        self.juice_config.set_custom_start_time(dt.strftime("%Y-%m-%dT%H:%M:%S"))
        return dt

    def _verify_file_existence(self) -> None:
        attitude_file = self.form.le_MappsAttitude.text()
        scenario_file = self.form.le_Scenario.text()
        timeline_file = self.form.le_MappsTimeline.text()
        for path in [attitude_file, scenario_file, timeline_file]:
            if not os.path.exists(path):
                raise ValueError("File: '{}' not found!".format(path))

    def _verify_scenario_file_location(self) -> Tuple[int, str]:
        """ Verifies whether the run_scenario.bat file will work, based on location
        of the original scenario JSON (which should be in
        <cosmographia_root>/JUICE/scenarios/), and whether <cosmographia_root> is
        in the system's PATH environment variable.

        :return: tuple in format (exit_code, exit_message)
            exit code: 0 - all good
                       1 - scenario file has wrong location
                       2 - cosmographia folder not in PATH
        """
        scenario_file_path = self.form.le_Scenario.text()
        scenario_folder_path, scenario_file = os.path.split(scenario_file_path)
        juice_folder_path, scenario_folder_name = os.path.split(scenario_folder_path)
        cosmographia_folder_path, juice_folder_name = os.path.split(juice_folder_path)
        error_message = (0, "")
        windows_paths = [os.path.abspath(s.strip('"')) for s in os.getenv("Path").split(';')]
        if not (os.path.exists(os.path.join(cosmographia_folder_path, 'Cosmographia.exe'))
                and juice_folder_name == "JUICE"
                and scenario_folder_name == "scenarios"):
            error_message = (
                1,
                "Scenario file is not placed in folder '<cosmographia_root_folder>\\JUICE\\scenarios\\'. "
                "It will not be possible to use the 'run_scenario.bat' script to launch the scenario.")
        elif os.path.abspath(cosmographia_folder_path) not in windows_paths:
            error_message = (
                2,
                "Cosmographia root folder '{}' not found in Windows PATH environment variable.".format(
                    cosmographia_folder_path.strip("\\")) +
                "It will not be possible to use the 'run_scenario.bat' script to launch the scenario.")
        return error_message

    def set_exit_message(self, msg: Tuple[int, str, str]) -> None:
        """ Stores exit message from TaskRunner thread for later display.

        :param msg: Message received by TaskRunner thread in format
        (exit_code, message)
        """
        self.exit_message = msg

    def loading_stop(self) -> None:
        """ Stops all threads and displays the last TaskRunner exit message.
        Prompts the user for input based on the error code of exit message
        """
        self.busy_widget.loading_stop()
        self.task_runner.quit()
        # if we had an error, display it
        if self.exit_message[0] != 0:
            response = QMessageBox.warning(self, "Error", self.exit_message[1],
                                           QMessageBox.Ok, QMessageBox.Ok)
            return
        # otherwise display dialog box based on .bat file status
        else:
            box = QMessageBox()
            box.setIcon(QMessageBox.Information)
            box.setWindowTitle("Success")
            box.setText(self.exit_message[1])
            # 3 options: launch cosmographia | exit script | do nothing
            if self.execute_bat_script:
                box.setStandardButtons(QMessageBox.Ok | QMessageBox.Ignore |
                                       QMessageBox.Cancel)
                b_launch = box.button(QMessageBox.Ok)
                b_launch.setText('Launch scenario')
                b_close = box.button(QMessageBox.Ignore)
                b_close.setText('Close program')
                b_donothing = box.button(QMessageBox.Cancel)
                b_donothing.setText('Do nothing')
                box.exec_()
                if box.clickedButton() == b_launch:
                    # Launch cosmographia
                    os.chdir(os.path.dirname(self.exit_message[2]))
                    os.startfile('run_scenario.bat')
                elif box.clickedButton() == b_close:
                    sys.exit(0)
                else:
                    return
            # 2 options: exit script | do nothing
            else:
                box.setStandardButtons(QMessageBox.Ignore |
                                       QMessageBox.Cancel)
                b_close = box.button(QMessageBox.Ignore)
                b_close.setText('Close program')
                b_donothing = box.button(QMessageBox.Cancel)
                b_donothing.setText('Do nothing')
                box.exec_()
                if box.clickedButton() == b_close:
                    sys.exit(0)
                else:
                    return

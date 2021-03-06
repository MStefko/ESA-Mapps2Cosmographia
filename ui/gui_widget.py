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
        self.form.le_Metakernel.setText(self.juice_config.get_last_scenario_folder())
        self.form.le_OutputFolderPath.setText(self.juice_config.get_last_output_path())
        self.form.le_OutputFolderName.setText(self.juice_config.get_last_output_folder())
        self.form.le_ObsDecayTimeMin.setText(str(self.juice_config.get_observation_lifetime()))

        self.form.cb_solarPanels.setChecked(self.juice_config.get_is_solar_panel_rotation_enabled())

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
        f = QFileDialog.getOpenFileName(self, "Open SPICE Metakernel", last_selection,
                                        "Metakernel files (*.mk, *.tm);;All files (*)")
        if f:
            file_name = str(f[0])
            self.juice_config.set_last_scenario_folder(file_name)
            self.form.le_Metakernel.setText(file_name)

    def browse_output_folder(self) -> None:
        last_selection = os.path.dirname(self.juice_config.get_last_output_path())
        f = QFileDialog.getExistingDirectory(self, "Choose output parent folder",
                                             last_selection, QFileDialog.ShowDirsOnly)
        if f:
            file_name = str(f)
            self.juice_config.set_last_output_path(file_name)
            self.form.le_OutputFolderPath.setText(file_name)

    def generate(self) -> None:
        """ Create the Working... mesage window, connect required thread signals together
        and start the TaskRunner thread.
        """
        # verify all three files exist
        try:
            self._verify_file_existence()
            self.parse_custom_start_time()
        except Exception as _:
            QMessageBox.warning(
                self, "File missing!", traceback.format_exc(0),
                QMessageBox.Ok, QMessageBox.Ok)
            traceback.print_exc()
            return

        # run the generation task
        self.task_runner = TaskRunner(self)
        self.busy_widget = WorkingMessage("Working")
        self.task_runner.set_message_function(self.busy_widget.set_message)
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
        scenario_file = self.form.le_Metakernel.text()
        timeline_file = self.form.le_MappsTimeline.text()
        output_path = self.form.le_OutputFolderPath.text()
        for path in [attitude_file, scenario_file, output_path]:
            if not os.path.exists(path):
                raise ValueError("File: '{}' not found!".format(path))
        if not os.path.exists(timeline_file) and len(timeline_file)>0:
            raise ValueError("MAPPS Timeline Dump field must point to a valid file or be empty.")
        if len(timeline_file) == 0 and self.form.cb_solarPanels.isChecked() and not self.form.cb_startTime.isChecked():
            raise ValueError("Start time override is mandatory when MAPPS Timeline Dump is missing and solar panels are computed.")
        if not os.path.isdir(output_path):
            raise ValueError("Output folder path '{}' must point to a folder".format(output_path))

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
        # otherwise display dialog box
        else:
            box = QMessageBox()
            box.setIcon(QMessageBox.Information)
            box.setWindowTitle("Success")
            box.setText(self.exit_message[1])
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
                if sys.platform == "win32":
                    os.startfile('run_scenario.bat')
                else:
                    os.startfile('run_scenario.sh')
            elif box.clickedButton() == b_close:
                sys.exit(0)
            else:
                return

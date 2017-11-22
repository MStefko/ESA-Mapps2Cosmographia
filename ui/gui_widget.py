import os
import sys
from collections import OrderedDict

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from attitude_converter import AttitudeConverter
from config import JuiceConfig
from worker_thread import TaskRunner, WorkingMessage
from ui.juice_win_converter import Ui_Form
from scenario_processor import ScenarioProcessor
from timeline_processor import TimelineProcessor


class MappsConverter(QWidget):

    def __init__(self, parent, juice_config):
        # type: (object, JuiceConfig) -> None
        """

        :param parent: Parent widget
        :param juice_config: JuiceConfig file
        """
        super(MappsConverter, self).__init__(parent)
        self.exit_message = "No exit message."
        self.juice_config = juice_config
        self.attitude_converter = AttitudeConverter()
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
        self.setMaximumSize(self.size())
        self.setMinimumSize(self.size())
        self.show()

    def _populate_instrument_table(self):
        # type: () -> None
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
            table.setItem(idx,0,item)
            self.instrument_checkboxes[name] = item

    def _parse_instrument_checkboxes(self):
        # type: () -> None
        """ Retrieves check values from GUI and informs the timeline processor and config. """
        checked_instruments = []
        for name, item in self.instrument_checkboxes.items():
            if item.checkState() == Qt.Checked:
                checked_instruments.append(name)
        self.juice_config.set_checked_instruments(checked_instruments)
        self.timeline_processor.set_instruments(checked_instruments)

    def browse_attitude(self):
        last_selection = os.path.dirname(self.juice_config.get_last_attitude_folder())
        f = QFileDialog.getOpenFileName(self, "Open Mapps Data File", last_selection, "CSV data files (*.csv)")
        if f:
            file_name = str(f[0])
            self.juice_config.set_last_attitude_folder(file_name)
            self.form.le_MappsAttitude.setText(file_name)
             
    def browse_timeline(self):
        last_selection = os.path.dirname(self.juice_config.get_last_timeline_folder())
        f = QFileDialog.getOpenFileName(self, "Open Mapps Timeline File", last_selection, "MAPPS timeline files (*.asc *.txt)")
        if f:
            file_name = str(f[0])
            self.juice_config.set_last_timeline_folder(file_name)
            self.form.le_MappsTimeline.setText(file_name)
             
    def browse_scenario(self):
        last_selection = os.path.dirname(self.juice_config.get_last_scenario_folder())
        f = QFileDialog.getOpenFileName(self, "Open Cosmographia Scenario File", last_selection, "Cosmographia scenario files (*.json)")
        if f:
            file_name = str(f[0])
            self.juice_config.set_last_scenario_folder(file_name)
            self.form.le_Scenario.setText(file_name)

    def generate(self):
        """ Create the Working... mesage window, connect required thread signals together
        and start the TaskRunner thread.
        """
        self.task_runner = TaskRunner(self)
        self.busy_widget = WorkingMessage("Working")
        self.task_runner.finished.connect(self.loading_stop)
        self.task_runner.start()
        self.busy_widget.show()


    def set_exit_message(self, msg):
        # type: (str) -> None
        """ Stores exit message from TaskRunner thread for later display.

        :param msg: Message received by TaskRunner thread
        """
        self.exit_message = msg

    def loading_stop(self):
        """ Stops all threads and displays the last TaskRunner exit message.
        If exit message of thread was successful, also exits the program.
        """
        self.busy_widget.loading_stop()
        self.task_runner.quit()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(self.exit_message)
        msg.exec_()
        if self.exit_message.startswith("Success"):
            sys.exit()
from collections import OrderedDict
import time
import os
import sys
import traceback

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from attitude_converter import AttitudeConverter
from juice_win_converter import Ui_Form
from scenario_processor import ScenarioProcessor
from timeline_processor import TimelineProcessor
from config import JuiceConfig


class MappsConverter(QWidget):

    def __init__(self, parent, juice_config):
        # type: (object, JuiceConfig) -> None
        """

        :param parent: Parent widget
        :param juice_config: JuiceConfig file
        """
        super(MappsConverter, self).__init__(parent)
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
        for name, item in self.instrument_checkboxes.iteritems():
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
        # type: () -> None
        """ Generates the scenario from inputs.
        First, parse all file names. Then, use MEX2KER to convert MAPPS attitude into
        a CK kernel. Generate a scenario using the MAPPS timeline, and put all necessary
        include files into the folder.
        """
        try:
            self._parse_instrument_checkboxes()
            target_name = self.form.comboBox_targetList.currentText()
            self.juice_config.set_selected_target(target_name)

            obs_lifetime_min = int(self.form.le_ObsDecayTimeMin.text())
            if obs_lifetime_min<0:
                raise ValueError("Observation decay time can't be negative.")
            self.timeline_processor.set_observation_lifetime_seconds(60*obs_lifetime_min)
            self.juice_config.set_observation_lifetime_min(obs_lifetime_min)

            ck_file_name = 'mapps_attitude_kernel.ck'
            attitude_file = self.form.le_MappsAttitude.text()
            scenario_file = self.form.le_Scenario.text()
            timeline_file = self.form.le_MappsTimeline.text()
            #if " " in scenario_file:
            #    raise ValueError("Cosmographia scenario folder path cannot contain a space. "
            #        "Please move entire JUICE Cosmographia folder to a location that does "
            #        "not contain a space in the path. This is a MEX2KER limitation.")

            scenario_folder = os.path.dirname(scenario_file)
            new_folder_name = 'mapps_output_' + time.strftime("%Y%m%d_%H%M%S")
            new_folder_path = os.path.abspath(os.path.join(scenario_folder,'..',new_folder_name))
            print "Creating scenario directory: {}".format(new_folder_path)
            os.makedirs(new_folder_path)

            output_ck_path = os.path.abspath(os.path.join(new_folder_path,ck_file_name))
            print "Generating CK kernel: {}".format(output_ck_path)
            self.attitude_converter.convert(attitude_file, output_ck_path)

            new_scenario_file_path = self.scenario_processor.process_scenario(
                scenario_file, new_folder_name, ck_file_name)
            print "Generating scenario file: {}".format(new_scenario_file_path)
            self.timeline_processor.process_scenario(target_name, timeline_file,
                                    new_scenario_file_path)
            print "Finished."
        except Exception as e:
            traceback.print_exc()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(traceback.format_exc(0) + "\nSee console for more details.")
            msg.exec_()
            return
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText('Scenario file generated at:\n\n{}'.format(new_scenario_file_path))
            msg.exec_()
from collections import OrderedDict

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from juice_win_converter import Ui_Form
import time
import os
import sys


class MappsConverter(QWidget):

    def __init__(self, parent, attitude_converter, scenario_processor,
                 timeline_processor, juice_config):
        super(MappsConverter, self).__init__(parent)
        self.juice_config = juice_config
        self.attitude_converter = attitude_converter
        self.scenario_processor = scenario_processor
        self.timeline_processor = timeline_processor
        self.form = Ui_Form()
        self.form.setupUi(self)
        self.form.l_version.setText(juice_config.get_version())
        self._populate_instrument_table()
        self.setMaximumSize(self.size())
        self.setMinimumSize(self.size())
        self.show()

    def _populate_instrument_table(self):
        table = self.form.instrumentTable
        instrument_list = self.juice_config.get_instruments()
        checked_instruments = self.juice_config.get_checked_instruments()
        self.instrument_checkboxes = OrderedDict()
        for idx, name in enumerate(instrument_list):
            item = QTableWidgetItem(name)
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            if name in checked_instruments:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            table.setItem(idx,0,item)
            self.instrument_checkboxes[name] = item

    def _parse_instrument_checkboxes(self):
        checked_instruments = []
        for name, item in self.instrument_checkboxes.iteritems():
            if item.checkState() == Qt.Checked:
                checked_instruments.append(name)
        self.juice_config.set_checked_instruments(checked_instruments)
        self.timeline_processor.set_instruments(checked_instruments)

    def browse_attitude(self):
        last_selection = self.juice_config.get_last_attitude_folder()
        f = QFileDialog.getOpenFileName(self, "Open Mapps Data File", last_selection, "CSV data files (*.csv)")
        if f:
            file_name = str(f[0])
            self.juice_config.set_last_attitude_folder(os.path.dirname(file_name))
            self.form.le_MappsAttitude.setText(file_name)
             
    def browse_timeline(self):
        last_selection = self.juice_config.get_last_timeline_folder()
        f = QFileDialog.getOpenFileName(self, "Open Mapps Timeline File", last_selection, "MAPPS timeline files (*.asc *.txt)")
        if f:
            file_name = str(f[0])
            self.juice_config.set_last_timeline_folder(os.path.dirname(file_name))
            self.form.le_MappsTimeline.setText(file_name)
             
    def browse_scenario(self):
        last_selection = self.juice_config.get_last_scenario_folder()
        f = QFileDialog.getOpenFileName(self, "Open Cosmographia Scenario File", last_selection, "Cosmographia scenario files (*.json)")
        if f:
            file_name = str(f[0])
            self.juice_config.set_last_scenario_folder(os.path.dirname(file_name))
            self.form.le_Scenario.setText(file_name)
             
    def generate(self):

        progress = QProgressDialog("Processing", "Abort", 0, 3, self)
        progress.setWindowModality(Qt.WindowModal)

        self._parse_instrument_checkboxes()
        ck_file_name = 'mapps_output.ck'
        attitude_file = self.form.le_MappsAttitude.text()
        scenario_file = self.form.le_Scenario.text()
        timeline_file = self.form.le_MappsTimeline.text()
        scenario_folder = os.path.dirname(scenario_file)
        new_folder_name = 'mapps_output_' + time.strftime("%Y%m%d_%H%M%S")
        new_folder_path = os.path.abspath(os.path.join(scenario_folder,'..',new_folder_name))
        os.makedirs(new_folder_path)
        output_ck_path = os.path.abspath(os.path.join(new_folder_path,ck_file_name))
        print output_ck_path
        progress.setValue(1)
        progress.forceShow()
        if progress.wasCanceled():
            return
        self.attitude_converter.convert(attitude_file, output_ck_path)
        progress.setValue(2)
        if progress.wasCanceled():
            return
        new_scenario_file_path = self.scenario_processor.process_scenario(
            scenario_file, new_folder_name, ck_file_name)

        self.timeline_processor.process_scenario(timeline_file,
                                new_scenario_file_path, new_folder_path)
        progress.destroy()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText('Scenario created')
        msg.exec_()
        sys.exit(0)
        return
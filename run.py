import os
import sys
import datetime, time
from PyQt5.QtWidgets import QApplication, QDialog

from scenario_processor import ScenarioProcessor
from timeline_processor import TimelineProcessor
from ui.gui_widget import MappsConverter
from sys import platform as _platform
from attitude_converter import AttitudeConverter

from config import JuiceConfig

if _platform == "win32":
    juice_plugin_path = os.path.abspath(
        os.path.join(os.path.abspath(__file__), '..'))
else:
    raise RuntimeError("Unsupported platform: {}".format(_platform))

        
juice_config = JuiceConfig(juice_plugin_path)

app = QApplication(sys.argv)
window = QDialog()
window.setWindowTitle("JUICE Plugin4Win")
ui = MappsConverter(window, juice_config)
window.show()
sys.exit(app.exec_())
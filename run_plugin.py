import os
import sys
from PyQt5.QtWidgets import QApplication, QDialog

from ui.gui_widget import MappsConverter
from sys import platform as _platform

from config import JuiceConfig

if _platform == "win32":
    juice_plugin_path = os.path.abspath(
        os.path.join(os.path.abspath(__file__), '..'))
else:
    raise RuntimeError("Unsupported platform: {}".format(_platform))
        
juice_config = JuiceConfig(juice_plugin_path)

app = QApplication(sys.argv)
# noinspection PyArgumentList
window = QDialog()
window.setWindowTitle("JUICE Plugin4Win")


def window_close_event(event):
    sys.exit()


window.closeEvent = window_close_event

ui = MappsConverter(window, juice_config)
window.show()
sys.exit(app.exec_())

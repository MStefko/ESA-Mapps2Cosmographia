import os
import sys


script_path = os.path.abspath(
    os.path.join(os.path.abspath(__file__), '..'))
if sys.version_info < (3, 5):
    raise RuntimeError("Unsupported Python version. Required >=3.5")

from PyQt5.QtWidgets import QApplication, QDialog
from ui.gui_widget import MappsConverter
from config import Config

config_ini = Config(script_path)

app = QApplication(sys.argv)
window = QDialog()
window.setWindowTitle("JUICE - Mapps2Cosmographia")


def window_close_event(_):
    sys.exit()


window.closeEvent = window_close_event

ui = MappsConverter(window, config_ini)
window.show()
sys.exit(app.exec_())

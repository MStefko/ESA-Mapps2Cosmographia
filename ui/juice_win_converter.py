# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'juice_win_converter.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

import ui.logo_rc


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(872, 551)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(20, 20, 151, 31))
        self.label.setObjectName("label")
        self.le_MappsAttitude = QtWidgets.QLineEdit(Form)
        self.le_MappsAttitude.setGeometry(QtCore.QRect(180, 20, 551, 31))
        self.le_MappsAttitude.setObjectName("le_MappsAttitude")
        self.pb_MappsAttitude = QtWidgets.QPushButton(Form)
        self.pb_MappsAttitude.setGeometry(QtCore.QRect(750, 20, 101, 31))
        self.pb_MappsAttitude.setObjectName("pb_MappsAttitude")
        self.pb_MappsTimeline = QtWidgets.QPushButton(Form)
        self.pb_MappsTimeline.setGeometry(QtCore.QRect(750, 60, 101, 31))
        self.pb_MappsTimeline.setObjectName("pb_MappsTimeline")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(20, 60, 151, 31))
        self.label_2.setObjectName("label_2")
        self.le_MappsTimeline = QtWidgets.QLineEdit(Form)
        self.le_MappsTimeline.setGeometry(QtCore.QRect(180, 60, 551, 31))
        self.le_MappsTimeline.setObjectName("le_MappsTimeline")
        self.pb_Metakernel = QtWidgets.QPushButton(Form)
        self.pb_Metakernel.setGeometry(QtCore.QRect(750, 100, 101, 31))
        self.pb_Metakernel.setObjectName("pb_Metakernel")
        self.le_Metakernel = QtWidgets.QLineEdit(Form)
        self.le_Metakernel.setGeometry(QtCore.QRect(180, 100, 551, 31))
        self.le_Metakernel.setObjectName("le_Metakernel")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(20, 100, 151, 31))
        self.label_3.setObjectName("label_3")
        self.pb_Generate = QtWidgets.QPushButton(Form)
        self.pb_Generate.setGeometry(QtCore.QRect(360, 500, 181, 31))
        self.pb_Generate.setObjectName("pb_Generate")
        self.l_version = QtWidgets.QLabel(Form)
        self.l_version.setGeometry(QtCore.QRect(740, 510, 111, 20))
        self.l_version.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.l_version.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.l_version.setObjectName("l_version")
        self.instrumentTable = QtWidgets.QTableWidget(Form)
        self.instrumentTable.setGeometry(QtCore.QRect(30, 290, 141, 241))
        self.instrumentTable.setShowGrid(True)
        self.instrumentTable.setRowCount(10)
        self.instrumentTable.setColumnCount(1)
        self.instrumentTable.setObjectName("instrumentTable")
        self.instrumentTable.horizontalHeader().setVisible(False)
        self.instrumentTable.verticalHeader().setVisible(True)
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setGeometry(QtCore.QRect(200, 290, 91, 31))
        self.label_4.setObjectName("label_4")
        self.comboBox_targetList = QtWidgets.QComboBox(Form)
        self.comboBox_targetList.setGeometry(QtCore.QRect(430, 290, 151, 31))
        self.comboBox_targetList.setObjectName("comboBox_targetList")
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setGeometry(QtCore.QRect(30, 250, 141, 31))
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(Form)
        self.label_6.setGeometry(QtCore.QRect(200, 340, 231, 31))
        self.label_6.setObjectName("label_6")
        self.le_ObsDecayTimeMin = QtWidgets.QLineEdit(Form)
        self.le_ObsDecayTimeMin.setGeometry(QtCore.QRect(510, 340, 71, 31))
        self.le_ObsDecayTimeMin.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.le_ObsDecayTimeMin.setObjectName("le_ObsDecayTimeMin")
        self.cb_startTime = QtWidgets.QCheckBox(Form)
        self.cb_startTime.setGeometry(QtCore.QRect(200, 390, 161, 31))
        self.cb_startTime.setObjectName("cb_startTime")
        self.le_StartTime = QtWidgets.QLineEdit(Form)
        self.le_StartTime.setEnabled(False)
        self.le_StartTime.setGeometry(QtCore.QRect(410, 390, 171, 31))
        self.le_StartTime.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.le_StartTime.setObjectName("le_StartTime")
        self.logo = QtWidgets.QLabel(Form)
        self.logo.setGeometry(QtCore.QRect(710, 420, 141, 111))
        self.logo.setScaledContents(False)
        self.logo.setAlignment(QtCore.Qt.AlignCenter)
        self.logo.setObjectName("logo")
        self.label_7 = QtWidgets.QLabel(Form)
        self.label_7.setGeometry(QtCore.QRect(20, 150, 151, 31))
        self.label_7.setObjectName("label_7")
        self.pb_OutputFolderPath = QtWidgets.QPushButton(Form)
        self.pb_OutputFolderPath.setGeometry(QtCore.QRect(750, 150, 101, 31))
        self.pb_OutputFolderPath.setObjectName("pb_OutputFolderPath")
        self.le_OutputFolderPath = QtWidgets.QLineEdit(Form)
        self.le_OutputFolderPath.setGeometry(QtCore.QRect(180, 150, 551, 31))
        self.le_OutputFolderPath.setText("")
        self.le_OutputFolderPath.setObjectName("le_OutputFolderPath")
        self.le_OutputFolderName = QtWidgets.QLineEdit(Form)
        self.le_OutputFolderName.setGeometry(QtCore.QRect(180, 190, 431, 31))
        self.le_OutputFolderName.setText("")
        self.le_OutputFolderName.setObjectName("le_OutputFolderName")
        self.label_8 = QtWidgets.QLabel(Form)
        self.label_8.setGeometry(QtCore.QRect(20, 190, 151, 31))
        self.label_8.setObjectName("label_8")
        self.cb_solarPanels = QtWidgets.QCheckBox(Form)
        self.cb_solarPanels.setGeometry(QtCore.QRect(200, 440, 151, 31))
        self.cb_solarPanels.setObjectName("cb_solarPanels")

        self.retranslateUi(Form)
        self.pb_MappsAttitude.clicked.connect(Form.browse_attitude)
        self.pb_MappsTimeline.clicked.connect(Form.browse_timeline)
        self.pb_Metakernel.clicked.connect(Form.browse_scenario)
        self.pb_Generate.clicked.connect(Form.generate)
        self.cb_startTime.stateChanged['int'].connect(Form.start_time_cb_changed)
        self.pb_OutputFolderPath.clicked.connect(Form.browse_output_folder)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "MAPPS Attitude Data:"))
        self.pb_MappsAttitude.setText(_translate("Form", "Browse"))
        self.pb_MappsTimeline.setText(_translate("Form", "Browse"))
        self.label_2.setText(_translate("Form", "MAPPS Timeline Dump:"))
        self.pb_Metakernel.setText(_translate("Form", "Browse"))
        self.label_3.setText(_translate("Form", "SPICE Metakernel:"))
        self.pb_Generate.setText(_translate("Form", "Generate files!"))
        self.l_version.setText(_translate("Form", "version"))
        self.label_4.setText(_translate("Form", "Target body:"))
        self.label_5.setText(_translate("Form", "Instruments"))
        self.label_6.setText(_translate("Form", "Observation decay time [min]:"))
        self.cb_startTime.setText(_translate("Form", "Custom start time:"))
        self.le_StartTime.setPlaceholderText(_translate("Form", "2031-04-25T22:45:47"))
        self.logo.setText(_translate("Form", "<html><head/><body><p><img src=\":/img/rsz_juice_insignia.png\"/></p></body></html>"))
        self.label_7.setText(_translate("Form", "Output folder path:"))
        self.pb_OutputFolderPath.setText(_translate("Form", "Browse"))
        self.label_8.setText(_translate("Form", "Output folder name:"))
        self.cb_solarPanels.setText(_translate("Form", "Solar panel rotation"))


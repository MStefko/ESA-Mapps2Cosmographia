# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'juice_win_converter.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(742, 443)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(20, 20, 151, 31))
        self.label.setObjectName("label")
        self.le_MappsAttitude = QtWidgets.QLineEdit(Form)
        self.le_MappsAttitude.setGeometry(QtCore.QRect(180, 20, 431, 31))
        self.le_MappsAttitude.setObjectName("le_MappsAttitude")
        self.pb_MappsAttitude = QtWidgets.QPushButton(Form)
        self.pb_MappsAttitude.setGeometry(QtCore.QRect(620, 20, 101, 31))
        self.pb_MappsAttitude.setObjectName("pb_MappsAttitude")
        self.pb_MappsTimeline = QtWidgets.QPushButton(Form)
        self.pb_MappsTimeline.setGeometry(QtCore.QRect(620, 70, 101, 31))
        self.pb_MappsTimeline.setObjectName("pb_MappsTimeline")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(20, 70, 151, 31))
        self.label_2.setObjectName("label_2")
        self.le_MappsTimeline = QtWidgets.QLineEdit(Form)
        self.le_MappsTimeline.setGeometry(QtCore.QRect(180, 70, 431, 31))
        self.le_MappsTimeline.setObjectName("le_MappsTimeline")
        self.pb_Scenario = QtWidgets.QPushButton(Form)
        self.pb_Scenario.setGeometry(QtCore.QRect(620, 120, 101, 31))
        self.pb_Scenario.setObjectName("pb_Scenario")
        self.le_Scenario = QtWidgets.QLineEdit(Form)
        self.le_Scenario.setGeometry(QtCore.QRect(180, 120, 431, 31))
        self.le_Scenario.setObjectName("le_Scenario")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(20, 120, 151, 31))
        self.label_3.setObjectName("label_3")
        self.pb_Generate = QtWidgets.QPushButton(Form)
        self.pb_Generate.setGeometry(QtCore.QRect(280, 390, 181, 31))
        self.pb_Generate.setObjectName("pb_Generate")
        self.l_version = QtWidgets.QLabel(Form)
        self.l_version.setGeometry(QtCore.QRect(620, 400, 111, 20))
        self.l_version.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.l_version.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.l_version.setObjectName("l_version")
        self.instrumentTable = QtWidgets.QTableWidget(Form)
        self.instrumentTable.setGeometry(QtCore.QRect(20, 170, 151, 192))
        self.instrumentTable.setRowCount(10)
        self.instrumentTable.setColumnCount(1)
        self.instrumentTable.setObjectName("instrumentTable")

        self.retranslateUi(Form)
        self.pb_MappsAttitude.clicked.connect(Form.browse_attitude)
        self.pb_MappsTimeline.clicked.connect(Form.browse_timeline)
        self.pb_Scenario.clicked.connect(Form.browse_scenario)
        self.pb_Generate.clicked.connect(Form.generate)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "MAPPS Attitude Data:"))
        self.pb_MappsAttitude.setText(_translate("Form", "Browse"))
        self.pb_MappsTimeline.setText(_translate("Form", "Browse"))
        self.label_2.setText(_translate("Form", "MAPPS Timeline Dump:"))
        self.pb_Scenario.setText(_translate("Form", "Browse"))
        self.label_3.setText(_translate("Form", "Cosmographia Scenario File:"))
        self.pb_Generate.setText(_translate("Form", "Generate files!"))
        self.l_version.setText(_translate("Form", "version"))


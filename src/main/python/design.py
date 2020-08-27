# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'form.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(249, 359)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.radioSort = QtWidgets.QRadioButton(self.centralwidget)
        self.radioSort.setObjectName("radioSort")
        self.gridLayout.addWidget(self.radioSort, 7, 0, 1, 1)
        self.lineEditInput = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditInput.setObjectName("lineEditInput")
        self.gridLayout.addWidget(self.lineEditInput, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButtonStart = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonStart.setObjectName("pushButtonStart")
        self.horizontalLayout.addWidget(self.pushButtonStart)
        self.gridLayout.addLayout(self.horizontalLayout, 11, 0, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.checkBoxBuReg = QtWidgets.QCheckBox(self.groupBox)
        self.checkBoxBuReg.setObjectName("checkBoxBuReg")
        self.gridLayout_2.addWidget(self.checkBoxBuReg, 2, 0, 1, 1)
        self.checkBoxSbReg = QtWidgets.QCheckBox(self.groupBox)
        self.checkBoxSbReg.setObjectName("checkBoxSbReg")
        self.gridLayout_2.addWidget(self.checkBoxSbReg, 4, 0, 1, 1)
        self.checkBoxBbReg = QtWidgets.QCheckBox(self.groupBox)
        self.checkBoxBbReg.setObjectName("checkBoxBbReg")
        self.gridLayout_2.addWidget(self.checkBoxBbReg, 5, 0, 1, 1)
        self.checkBoxBbFish = QtWidgets.QCheckBox(self.groupBox)
        self.checkBoxBbFish.setObjectName("checkBoxBbFish")
        self.gridLayout_2.addWidget(self.checkBoxBbFish, 5, 1, 1, 1)
        self.checkBoxSbFish = QtWidgets.QCheckBox(self.groupBox)
        self.checkBoxSbFish.setObjectName("checkBoxSbFish")
        self.gridLayout_2.addWidget(self.checkBoxSbFish, 4, 1, 1, 1)
        self.checkBoxBuFish = QtWidgets.QCheckBox(self.groupBox)
        self.checkBoxBuFish.setObjectName("checkBoxBuFish")
        self.gridLayout_2.addWidget(self.checkBoxBuFish, 2, 1, 1, 1)
        self.checkBoxCoReg = QtWidgets.QCheckBox(self.groupBox)
        self.checkBoxCoReg.setObjectName("checkBoxCoReg")
        self.gridLayout_2.addWidget(self.checkBoxCoReg, 1, 0, 1, 1)
        self.checkBoxCoFish = QtWidgets.QCheckBox(self.groupBox)
        self.checkBoxCoFish.setObjectName("checkBoxCoFish")
        self.gridLayout_2.addWidget(self.checkBoxCoFish, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 10, 0, 1, 1)
        self.toolButtonInput = QtWidgets.QToolButton(self.centralwidget)
        self.toolButtonInput.setObjectName("toolButtonInput")
        self.gridLayout.addWidget(self.toolButtonInput, 0, 1, 1, 1)
        self.lineEditOutput = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditOutput.setObjectName("lineEditOutput")
        self.gridLayout.addWidget(self.lineEditOutput, 1, 0, 1, 1)
        self.toolButtonOutput = QtWidgets.QToolButton(self.centralwidget)
        self.toolButtonOutput.setObjectName("toolButtonOutput")
        self.gridLayout.addWidget(self.toolButtonOutput, 1, 1, 1, 1)
        self.radioSplit = QtWidgets.QRadioButton(self.centralwidget)
        self.radioSplit.setObjectName("radioSplit")
        self.gridLayout.addWidget(self.radioSplit, 3, 0, 1, 1)
        self.radioEv = QtWidgets.QRadioButton(self.centralwidget)
        self.radioEv.setObjectName("radioEv")
        self.gridLayout.addWidget(self.radioEv, 8, 0, 1, 1)
        self.radioCsv = QtWidgets.QRadioButton(self.centralwidget)
        self.radioCsv.setObjectName("radioCsv")
        self.gridLayout.addWidget(self.radioCsv, 9, 0, 1, 1)
        self.lineEditNotes = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditNotes.setObjectName("lineEditNotes")
        self.gridLayout.addWidget(self.lineEditNotes, 2, 0, 1, 1)
        self.toolButtonNotes = QtWidgets.QToolButton(self.centralwidget)
        self.toolButtonNotes.setObjectName("toolButtonNotes")
        self.gridLayout.addWidget(self.toolButtonNotes, 2, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "HandProc"))
        self.radioSort.setText(_translate("MainWindow", "Sort hands by tournament positions"))
        self.pushButtonStart.setText(_translate("MainWindow", "Start"))
        self.groupBox.setTitle(_translate("MainWindow", "Filters"))
        self.checkBoxBuReg.setText(_translate("MainWindow", "BU reg"))
        self.checkBoxSbReg.setText(_translate("MainWindow", "SB reg"))
        self.checkBoxBbReg.setText(_translate("MainWindow", "BB reg"))
        self.checkBoxBbFish.setText(_translate("MainWindow", "BB fish"))
        self.checkBoxSbFish.setText(_translate("MainWindow", "SB fish"))
        self.checkBoxBuFish.setText(_translate("MainWindow", "BU fish"))
        self.checkBoxCoReg.setText(_translate("MainWindow", "CO reg"))
        self.checkBoxCoFish.setText(_translate("MainWindow", "CO fish"))
        self.toolButtonInput.setText(_translate("MainWindow", "in"))
        self.toolButtonOutput.setText(_translate("MainWindow", "out"))
        self.radioSplit.setText(_translate("MainWindow", "Split satellit hand history files"))
        self.radioEv.setText(_translate("MainWindow", "Fix hands for EV calculating"))
        self.radioCsv.setText(_translate("MainWindow", "Save summary to csv file"))
        self.toolButtonNotes.setText(_translate("MainWindow", "notes"))

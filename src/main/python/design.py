# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'form2.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(243, 632)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setMaximumSize(QtCore.QSize(16777215, 117))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.formLayout_3 = QtWidgets.QFormLayout(self.tab)
        self.formLayout_3.setObjectName("formLayout_3")
        self.toolButtonInput = QtWidgets.QToolButton(self.tab)
        self.toolButtonInput.setObjectName("toolButtonInput")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.toolButtonInput)
        self.lineEditInput = QtWidgets.QLineEdit(self.tab)
        self.lineEditInput.setObjectName("lineEditInput")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEditInput)
        self.toolButtonOutput = QtWidgets.QToolButton(self.tab)
        self.toolButtonOutput.setObjectName("toolButtonOutput")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.toolButtonOutput)
        self.lineEditOutput = QtWidgets.QLineEdit(self.tab)
        self.lineEditOutput.setObjectName("lineEditOutput")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEditOutput)
        self.toolButtonNotes = QtWidgets.QToolButton(self.tab)
        self.toolButtonNotes.setObjectName("toolButtonNotes")
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.toolButtonNotes)
        self.lineEditNotes = QtWidgets.QLineEdit(self.tab)
        self.lineEditNotes.setObjectName("lineEditNotes")
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.lineEditNotes)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setMinimumSize(QtCore.QSize(0, 69))
        self.groupBox_2.setMaximumSize(QtCore.QSize(16777215, 69))
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout.addWidget(self.label_4)
        self.spinBoxBiFrom = QtWidgets.QSpinBox(self.groupBox_2)
        self.spinBoxBiFrom.setMaximum(2000)
        self.spinBoxBiFrom.setProperty("value", 7)
        self.spinBoxBiFrom.setObjectName("spinBoxBiFrom")
        self.horizontalLayout.addWidget(self.spinBoxBiFrom)
        self.label_5 = QtWidgets.QLabel(self.groupBox_2)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout.addWidget(self.label_5)
        self.spinBoxBiTo = QtWidgets.QSpinBox(self.groupBox_2)
        self.spinBoxBiTo.setMaximum(2000)
        self.spinBoxBiTo.setProperty("value", 15)
        self.spinBoxBiTo.setObjectName("spinBoxBiTo")
        self.horizontalLayout.addWidget(self.spinBoxBiTo)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 97))
        self.groupBox.setObjectName("groupBox")
        self.formLayout_2 = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.dteFrom = QtWidgets.QDateTimeEdit(self.groupBox)
        self.dteFrom.setDate(QtCore.QDate(2021, 1, 1))
        self.dteFrom.setCalendarPopup(True)
        self.dteFrom.setObjectName("dteFrom")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.dteFrom)
        self.dteTo = QtWidgets.QDateTimeEdit(self.groupBox)
        self.dteTo.setDate(QtCore.QDate(2021, 1, 1))
        self.dteTo.setCalendarPopup(True)
        self.dteTo.setObjectName("dteTo")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.dteTo)
        self.verticalLayout.addWidget(self.groupBox)
        self.radioSplit = QtWidgets.QRadioButton(self.centralwidget)
        self.radioSplit.setChecked(True)
        self.radioSplit.setObjectName("radioSplit")
        self.verticalLayout.addWidget(self.radioSplit)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.checkBoxSort = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBoxSort.setMaximumSize(QtCore.QSize(16777215, 17))
        self.checkBoxSort.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.checkBoxSort.setAutoFillBackground(False)
        self.checkBoxSort.setChecked(True)
        self.checkBoxSort.setObjectName("checkBoxSort")
        self.horizontalLayout_2.addWidget(self.checkBoxSort)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.radioEv = QtWidgets.QRadioButton(self.centralwidget)
        self.radioEv.setObjectName("radioEv")
        self.verticalLayout.addWidget(self.radioEv)
        self.radioCsv = QtWidgets.QRadioButton(self.centralwidget)
        self.radioCsv.setObjectName("radioCsv")
        self.verticalLayout.addWidget(self.radioCsv)
        self.gbFilters = QtWidgets.QGroupBox(self.centralwidget)
        self.gbFilters.setMaximumSize(QtCore.QSize(16777215, 119))
        self.gbFilters.setObjectName("gbFilters")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gbFilters)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.checkBoxBuReg = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxBuReg.setObjectName("checkBoxBuReg")
        self.gridLayout_2.addWidget(self.checkBoxBuReg, 2, 0, 1, 1)
        self.checkBoxSbReg = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxSbReg.setObjectName("checkBoxSbReg")
        self.gridLayout_2.addWidget(self.checkBoxSbReg, 4, 0, 1, 1)
        self.checkBoxBbReg = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxBbReg.setObjectName("checkBoxBbReg")
        self.gridLayout_2.addWidget(self.checkBoxBbReg, 5, 0, 1, 1)
        self.checkBoxBbFish = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxBbFish.setObjectName("checkBoxBbFish")
        self.gridLayout_2.addWidget(self.checkBoxBbFish, 5, 1, 1, 1)
        self.checkBoxSbFish = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxSbFish.setObjectName("checkBoxSbFish")
        self.gridLayout_2.addWidget(self.checkBoxSbFish, 4, 1, 1, 1)
        self.checkBoxBuFish = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxBuFish.setObjectName("checkBoxBuFish")
        self.gridLayout_2.addWidget(self.checkBoxBuFish, 2, 1, 1, 1)
        self.checkBoxCoReg = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxCoReg.setObjectName("checkBoxCoReg")
        self.gridLayout_2.addWidget(self.checkBoxCoReg, 1, 0, 1, 1)
        self.checkBoxCoFish = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxCoFish.setObjectName("checkBoxCoFish")
        self.gridLayout_2.addWidget(self.checkBoxCoFish, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.gbFilters)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.pushButtonStart = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonStart.setObjectName("pushButtonStart")
        self.verticalLayout.addWidget(self.pushButtonStart)
        self.writerLabel = QtWidgets.QLabel(self.centralwidget)
        self.writerLabel.setText("")
        self.writerLabel.setObjectName("writerLabel")
        self.verticalLayout.addWidget(self.writerLabel)
        self.processorLabel = QtWidgets.QLabel(self.centralwidget)
        self.processorLabel.setText("")
        self.processorLabel.setObjectName("processorLabel")
        self.verticalLayout.addWidget(self.processorLabel)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 243, 21))
        self.menuBar.setObjectName("menuBar")
        self.menuabout = QtWidgets.QMenu(self.menuBar)
        self.menuabout.setObjectName("menuabout")
        MainWindow.setMenuBar(self.menuBar)
        self.actionVersion_0_1_0 = QtWidgets.QAction(MainWindow)
        self.actionVersion_0_1_0.setObjectName("actionVersion_0_1_0")
        self.menuabout.addAction(self.actionVersion_0_1_0)
        self.menuBar.addAction(self.menuabout.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "HandProc"))
        self.toolButtonInput.setText(_translate("MainWindow", "in"))
        self.toolButtonOutput.setText(_translate("MainWindow", "out"))
        self.toolButtonNotes.setText(_translate("MainWindow", "notes"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Folders"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "H2N"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Buyins"))
        self.label_4.setText(_translate("MainWindow", "From"))
        self.label_5.setText(_translate("MainWindow", "To"))
        self.groupBox.setTitle(_translate("MainWindow", "Starting date and time of tournaments"))
        self.label.setText(_translate("MainWindow", "From"))
        self.label_2.setText(_translate("MainWindow", "To"))
        self.radioSplit.setText(_translate("MainWindow", "Split satellit hand history files"))
        self.checkBoxSort.setText(_translate("MainWindow", "sort round2 hands by positions"))
        self.radioEv.setText(_translate("MainWindow", "Fix hands for EV calculating"))
        self.radioCsv.setText(_translate("MainWindow", "Save summary to csv file"))
        self.gbFilters.setTitle(_translate("MainWindow", "Filters"))
        self.checkBoxBuReg.setText(_translate("MainWindow", "BU reg"))
        self.checkBoxSbReg.setText(_translate("MainWindow", "SB reg"))
        self.checkBoxBbReg.setText(_translate("MainWindow", "BB reg"))
        self.checkBoxBbFish.setText(_translate("MainWindow", "BB fish"))
        self.checkBoxSbFish.setText(_translate("MainWindow", "SB fish"))
        self.checkBoxBuFish.setText(_translate("MainWindow", "BU fish"))
        self.checkBoxCoReg.setText(_translate("MainWindow", "CO reg"))
        self.checkBoxCoFish.setText(_translate("MainWindow", "CO fish"))
        self.pushButtonStart.setText(_translate("MainWindow", "Start"))
        self.menuabout.setTitle(_translate("MainWindow", "about"))
        self.actionVersion_0_1_0.setText(_translate("MainWindow", "Version 0.2.0"))

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
        MainWindow.resize(314, 790)
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
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.lineEditDBName = QtWidgets.QLineEdit(self.tab_2)
        self.lineEditDBName.setGeometry(QtCore.QRect(13, 11, 133, 20))
        self.lineEditDBName.setObjectName("lineEditDBName")
        self.pushButtonTestConn = QtWidgets.QPushButton(self.tab_2)
        self.pushButtonTestConn.setGeometry(QtCore.QRect(150, 10, 51, 21))
        self.pushButtonTestConn.setObjectName("pushButtonTestConn")
        self.tabWidget.addTab(self.tab_2, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.formLayout.setObjectName("formLayout")
        self.toolButtonOutput = QtWidgets.QToolButton(self.centralwidget)
        self.toolButtonOutput.setObjectName("toolButtonOutput")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.toolButtonOutput)
        self.lineEditOutput = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditOutput.setObjectName("lineEditOutput")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEditOutput)
        self.toolButtonNotes = QtWidgets.QToolButton(self.centralwidget)
        self.toolButtonNotes.setObjectName("toolButtonNotes")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.toolButtonNotes)
        self.lineEditNotes = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditNotes.setObjectName("lineEditNotes")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEditNotes)
        self.verticalLayout.addLayout(self.formLayout)
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
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.checkBoxSort = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBoxSort.setMaximumSize(QtCore.QSize(16777215, 17))
        self.checkBoxSort.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.checkBoxSort.setAutoFillBackground(False)
        self.checkBoxSort.setChecked(False)
        self.checkBoxSort.setObjectName("checkBoxSort")
        self.horizontalLayout_2.addWidget(self.checkBoxSort)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.radioEv = QtWidgets.QRadioButton(self.centralwidget)
        self.radioEv.setObjectName("radioEv")
        self.verticalLayout.addWidget(self.radioEv)
        self.gbFilters = QtWidgets.QGroupBox(self.centralwidget)
        self.gbFilters.setObjectName("gbFilters")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gbFilters)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.checkBoxBuNotCoversSBBB = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxBuNotCoversSBBB.setObjectName("checkBoxBuNotCoversSBBB")
        self.gridLayout_2.addWidget(self.checkBoxBuNotCoversSBBB, 7, 1, 1, 1)
        self.checkBoxBuCoversSBnotBB = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxBuCoversSBnotBB.setObjectName("checkBoxBuCoversSBnotBB")
        self.gridLayout_2.addWidget(self.checkBoxBuCoversSBnotBB, 8, 1, 1, 1)
        self.checkBoxBuCoversBBNotSB = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxBuCoversBBNotSB.setObjectName("checkBoxBuCoversBBNotSB")
        self.gridLayout_2.addWidget(self.checkBoxBuCoversBBNotSB, 8, 0, 1, 1)
        self.checkBoxCOCoversSBBB = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxCOCoversSBBB.setObjectName("checkBoxCOCoversSBBB")
        self.gridLayout_2.addWidget(self.checkBoxCOCoversSBBB, 13, 1, 1, 1)
        self.checkBoxCOCoversBUSB = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxCOCoversBUSB.setObjectName("checkBoxCOCoversBUSB")
        self.gridLayout_2.addWidget(self.checkBoxCOCoversBUSB, 13, 0, 1, 1)
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
        self.checkBoxBuCoversSBBB = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxBuCoversSBBB.setObjectName("checkBoxBuCoversSBBB")
        self.gridLayout_2.addWidget(self.checkBoxBuCoversSBBB, 7, 0, 1, 1)
        self.checkBoxBuReg = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxBuReg.setObjectName("checkBoxBuReg")
        self.gridLayout_2.addWidget(self.checkBoxBuReg, 2, 0, 1, 1)
        self.checkBoxCOCoversBUBB = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxCOCoversBUBB.setObjectName("checkBoxCOCoversBUBB")
        self.gridLayout_2.addWidget(self.checkBoxCOCoversBUBB, 14, 0, 1, 1)
        self.checkBoxCOCoversBUSBBB = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxCOCoversBUSBBB.setObjectName("checkBoxCOCoversBUSBBB")
        self.gridLayout_2.addWidget(self.checkBoxCOCoversBUSBBB, 12, 0, 1, 1)
        self.line = QtWidgets.QFrame(self.gbFilters)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_2.addWidget(self.line, 11, 0, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.gbFilters)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout_2.addWidget(self.line_2, 6, 0, 1, 1)
        self.checkBoxCONotCoversBUSBBB = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxCONotCoversBUSBBB.setObjectName("checkBoxCONotCoversBUSBBB")
        self.gridLayout_2.addWidget(self.checkBoxCONotCoversBUSBBB, 12, 1, 1, 1)
        self.checkBoxCOCoversBU = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxCOCoversBU.setObjectName("checkBoxCOCoversBU")
        self.gridLayout_2.addWidget(self.checkBoxCOCoversBU, 15, 0, 1, 1)
        self.checkBoxCOCoversSB = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxCOCoversSB.setObjectName("checkBoxCOCoversSB")
        self.gridLayout_2.addWidget(self.checkBoxCOCoversSB, 15, 1, 1, 1)
        self.checkBoxCOCoversBB = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxCOCoversBB.setObjectName("checkBoxCOCoversBB")
        self.gridLayout_2.addWidget(self.checkBoxCOCoversBB, 14, 1, 1, 1)

        self.checkBoxUTGCoversAll = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxUTGCoversAll.setObjectName("checkBoxUTGCoversAll")
        self.gridLayout_2.addWidget(self.checkBoxUTGCoversAll, 16, 0, 1, 1)
        self.checkBoxUTGNotCoversAll = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxUTGNotCoversAll.setObjectName("checkBoxUTGNotCoversAll ")
        self.gridLayout_2.addWidget(self.checkBoxUTGNotCoversAll, 16, 1, 1, 1)

        self.checkBoxMPCoversAll = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxMPCoversAll.setObjectName("checkBoxMPCoversAll")
        self.gridLayout_2.addWidget(self.checkBoxMPCoversAll, 17, 0, 1, 1)
        self.checkBoxMPNotCoversAll = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxMPNotCoversAll.setObjectName("checkBoxMPNotCoversAll ")
        self.gridLayout_2.addWidget(self.checkBoxMPNotCoversAll, 17, 1, 1, 1)

        self.checkBoxEPCoversAll = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxEPCoversAll.setObjectName("checkBoxEPCoversAll")
        self.gridLayout_2.addWidget(self.checkBoxEPCoversAll, 18, 0, 1, 1)
        self.checkBoxEPNotCoversAll = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxEPNotCoversAll.setObjectName("checkBoxEPNotCoversAll ")
        self.gridLayout_2.addWidget(self.checkBoxEPNotCoversAll, 18, 1, 1, 1)

        self.checkBoxLJCoversAll = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxLJCoversAll.setObjectName("checkBoxLJCoversAll")
        self.gridLayout_2.addWidget(self.checkBoxLJCoversAll, 19, 0, 1, 1)
        self.checkBoxLJNotCoversAll = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxLJNotCoversAll.setObjectName("checkBoxLJNotCoversAll ")
        self.gridLayout_2.addWidget(self.checkBoxLJNotCoversAll, 19, 1, 1, 1)

        self.checkBoxHJCoversAll = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxHJCoversAll.setObjectName("checkBoxHJCoversAll")
        self.gridLayout_2.addWidget(self.checkBoxHJCoversAll, 20, 0, 1, 1)
        self.checkBoxHJNotCoversAll = QtWidgets.QCheckBox(self.gbFilters)
        self.checkBoxHJNotCoversAll.setObjectName("checkBoxHJNotCoversAll ")
        self.gridLayout_2.addWidget(self.checkBoxHJNotCoversAll, 20, 1, 1, 1)

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
        self.actionVersion_0_1_0 = QtWidgets.QAction(MainWindow)
        self.actionVersion_0_1_0.setObjectName("actionVersion_0_1_0")

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "HandProc"))
        self.toolButtonInput.setText(_translate("MainWindow", "in"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Folders"))
        self.pushButtonTestConn.setText(_translate("MainWindow", "Connect"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "H2N"))
        self.toolButtonOutput.setText(_translate("MainWindow", "out"))
        self.toolButtonNotes.setText(_translate("MainWindow", "notes"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Buyins"))
        self.label_4.setText(_translate("MainWindow", "From"))
        self.label_5.setText(_translate("MainWindow", "To"))
        self.groupBox.setTitle(_translate("MainWindow", "Starting date and time of tournaments"))
        self.label.setText(_translate("MainWindow", "From"))
        self.label_2.setText(_translate("MainWindow", "To"))
        self.radioSplit.setText(_translate("MainWindow", "Split satellit hand history files"))
        self.checkBoxSort.setText(_translate("MainWindow", "sort ROUND1 hands by positions"))
        self.radioEv.setText(_translate("MainWindow", "Fix hands for EV calculating"))
        self.gbFilters.setTitle(_translate("MainWindow", "Filters"))
        self.checkBoxBuNotCoversSBBB.setText(_translate("MainWindow", "BU NOT covers BB, SB"))
        self.checkBoxBuCoversSBnotBB.setText(_translate("MainWindow", "BU covers SB NOT BB"))
        self.checkBoxBuCoversBBNotSB.setText(_translate("MainWindow", "BU covers BB NOT SB"))
        self.checkBoxCOCoversSBBB.setText(_translate("MainWindow", "CO covers SB,BB"))
        self.checkBoxCOCoversBUSB.setText(_translate("MainWindow", "CO covers BU, SB"))
        self.checkBoxSbReg.setText(_translate("MainWindow", "SB reg"))
        self.checkBoxBbReg.setText(_translate("MainWindow", "BB reg"))
        self.checkBoxBbFish.setText(_translate("MainWindow", "BB fish"))
        self.checkBoxSbFish.setText(_translate("MainWindow", "SB fish"))
        self.checkBoxBuFish.setText(_translate("MainWindow", "BU fish"))
        self.checkBoxCoReg.setText(_translate("MainWindow", "CO reg"))
        self.checkBoxCoFish.setText(_translate("MainWindow", "CO fish"))
        self.checkBoxBuCoversSBBB.setText(_translate("MainWindow", "BU covers BB, SB"))
        self.checkBoxBuReg.setText(_translate("MainWindow", "BU reg"))
        self.checkBoxCOCoversBUBB.setText(_translate("MainWindow", "CO covers BU, BB"))
        self.checkBoxCOCoversBUSBBB.setText(_translate("MainWindow", "CO covers BU,SB,BB"))
        self.checkBoxCONotCoversBUSBBB.setText(_translate("MainWindow", "CO NOT covers BU,SB,BB"))
        self.checkBoxCOCoversBU.setText(_translate("MainWindow", "CO covers BU"))
        self.checkBoxCOCoversSB.setText(_translate("MainWindow", "CO covers SB"))
        self.checkBoxCOCoversBB.setText(_translate("MainWindow", "CO covers BB"))

        self.checkBoxUTGCoversAll.setText(_translate("MainWindow", "UTG covers All"))
        self.checkBoxUTGNotCoversAll.setText(_translate("MainWindow", "UTG not covers All"))

        self.checkBoxMPCoversAll.setText(_translate("MainWindow", "MP covers All"))
        self.checkBoxMPNotCoversAll.setText(_translate("MainWindow", "MP not covers All"))

        self.checkBoxEPCoversAll.setText(_translate("MainWindow", "EP covers All"))
        self.checkBoxEPNotCoversAll.setText(_translate("MainWindow", "EP not covers All"))

        self.checkBoxLJCoversAll.setText(_translate("MainWindow", "LJ covers All"))
        self.checkBoxLJNotCoversAll.setText(_translate("MainWindow", "LJ not covers All"))

        self.checkBoxHJCoversAll.setText(_translate("MainWindow", "HJ covers All"))
        self.checkBoxHJNotCoversAll.setText(_translate("MainWindow", "HJ not covers All"))

        self.pushButtonStart.setText(_translate("MainWindow", "Start"))
        self.actionVersion_0_1_0.setText(_translate("MainWindow", "Version 0.2.0"))
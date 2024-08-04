# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'paste_board.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QGridLayout,
    QHBoxLayout, QLabel, QPlainTextEdit, QProgressBar,
    QPushButton, QSizePolicy, QSpacerItem, QSpinBox,
    QTabWidget, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.setWindowModality(Qt.WindowModal)
        Dialog.resize(400, 364)
        Dialog.setMaximumSize(QSize(999999, 999999))
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tabWidget = QTabWidget(Dialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setAcceptDrops(True)
        self.tab_1 = QWidget()
        self.tab_1.setObjectName(u"tab_1")
        self.verticalLayout = QVBoxLayout(self.tab_1)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.plainTextEdit_1 = QPlainTextEdit(self.tab_1)
        self.plainTextEdit_1.setObjectName(u"plainTextEdit_1")

        self.verticalLayout.addWidget(self.plainTextEdit_1)

        self.tabWidget.addTab(self.tab_1, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_2 = QVBoxLayout(self.tab_2)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.plainTextEdit_2 = QPlainTextEdit(self.tab_2)
        self.plainTextEdit_2.setObjectName(u"plainTextEdit_2")

        self.verticalLayout_2.addWidget(self.plainTextEdit_2)

        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.verticalLayout_3 = QVBoxLayout(self.tab_3)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.plainTextEdit_3 = QPlainTextEdit(self.tab_3)
        self.plainTextEdit_3.setObjectName(u"plainTextEdit_3")

        self.verticalLayout_3.addWidget(self.plainTextEdit_3)

        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.verticalLayout_4 = QVBoxLayout(self.tab_4)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.plainTextEdit_4 = QPlainTextEdit(self.tab_4)
        self.plainTextEdit_4.setObjectName(u"plainTextEdit_4")

        self.verticalLayout_4.addWidget(self.plainTextEdit_4)

        self.tabWidget.addTab(self.tab_4, "")
        self.tab_5 = QWidget()
        self.tab_5.setObjectName(u"tab_5")
        self.verticalLayout_5 = QVBoxLayout(self.tab_5)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.plainTextEdit_5 = QPlainTextEdit(self.tab_5)
        self.plainTextEdit_5.setObjectName(u"plainTextEdit_5")

        self.verticalLayout_5.addWidget(self.plainTextEdit_5)

        self.tabWidget.addTab(self.tab_5, "")
        self.tab_6 = QWidget()
        self.tab_6.setObjectName(u"tab_6")
        self.verticalLayout_6 = QVBoxLayout(self.tab_6)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.plainTextEdit_6 = QPlainTextEdit(self.tab_6)
        self.plainTextEdit_6.setObjectName(u"plainTextEdit_6")

        self.verticalLayout_6.addWidget(self.plainTextEdit_6)

        self.tabWidget.addTab(self.tab_6, "")
        self.tab_7 = QWidget()
        self.tab_7.setObjectName(u"tab_7")
        self.verticalLayout_7 = QVBoxLayout(self.tab_7)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.plainTextEdit_7 = QPlainTextEdit(self.tab_7)
        self.plainTextEdit_7.setObjectName(u"plainTextEdit_7")

        self.verticalLayout_7.addWidget(self.plainTextEdit_7)

        self.tabWidget.addTab(self.tab_7, "")
        self.tab_8 = QWidget()
        self.tab_8.setObjectName(u"tab_8")
        self.verticalLayout_8 = QVBoxLayout(self.tab_8)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.plainTextEdit_8 = QPlainTextEdit(self.tab_8)
        self.plainTextEdit_8.setObjectName(u"plainTextEdit_8")

        self.verticalLayout_8.addWidget(self.plainTextEdit_8)

        self.tabWidget.addTab(self.tab_8, "")
        self.tab_9 = QWidget()
        self.tab_9.setObjectName(u"tab_9")
        self.verticalLayout_9 = QVBoxLayout(self.tab_9)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.plainTextEdit_9 = QPlainTextEdit(self.tab_9)
        self.plainTextEdit_9.setObjectName(u"plainTextEdit_9")

        self.verticalLayout_9.addWidget(self.plainTextEdit_9)

        self.tabWidget.addTab(self.tab_9, "")
        self.tab_f = QWidget()
        self.tab_f.setObjectName(u"tab_f")
        self.tab_f.setAcceptDrops(True)
        self.verticalLayout_10 = QVBoxLayout(self.tab_f)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.label = QLabel(self.tab_f)
        self.label.setObjectName(u"label")
        self.label.setAcceptDrops(True)
        self.label.setTextFormat(Qt.MarkdownText)
        self.label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.label.setMargin(0)
        self.label.setIndent(0)

        self.verticalLayout_10.addWidget(self.label)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer)

        self.label_2 = QLabel(self.tab_f)
        self.label_2.setObjectName(u"label_2")
        font = QFont()
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setAcceptDrops(True)

        self.verticalLayout_10.addWidget(self.label_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 4, -1, 4)
        self.labelFile = QLabel(self.tab_f)
        self.labelFile.setObjectName(u"labelFile")
        self.labelFile.setAcceptDrops(True)

        self.horizontalLayout.addWidget(self.labelFile)

        self.pushButtonFile = QPushButton(self.tab_f)
        self.pushButtonFile.setObjectName(u"pushButtonFile")

        self.horizontalLayout.addWidget(self.pushButtonFile)

        self.horizontalLayout.setStretch(0, 1)

        self.verticalLayout_10.addLayout(self.horizontalLayout)

        self.progressBar = QProgressBar(self.tab_f)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)

        self.verticalLayout_10.addWidget(self.progressBar)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer_2)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(-1, 4, -1, 4)
        self.checkBoxEcho = QCheckBox(self.tab_f)
        self.checkBoxEcho.setObjectName(u"checkBoxEcho")

        self.horizontalLayout_7.addWidget(self.checkBoxEcho)


        self.verticalLayout_10.addLayout(self.horizontalLayout_7)

        self.tabWidget.addTab(self.tab_f, "")
        self.tab_set = QWidget()
        self.tab_set.setObjectName(u"tab_set")
        self.verticalLayout_12 = QVBoxLayout(self.tab_set)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_3 = QLabel(self.tab_set)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_3.addWidget(self.label_3)

        self.spinBox_ci = QSpinBox(self.tab_set)
        self.spinBox_ci.setObjectName(u"spinBox_ci")
        self.spinBox_ci.setMaximum(1000)

        self.horizontalLayout_3.addWidget(self.spinBox_ci)


        self.verticalLayout_12.addLayout(self.horizontalLayout_3)

        self.label_9 = QLabel(self.tab_set)
        self.label_9.setObjectName(u"label_9")

        self.verticalLayout_12.addWidget(self.label_9)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_6 = QLabel(self.tab_set)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_6.addWidget(self.label_6)

        self.spinBox_ps = QSpinBox(self.tab_set)
        self.spinBox_ps.setObjectName(u"spinBox_ps")
        self.spinBox_ps.setMaximum(102400)

        self.horizontalLayout_6.addWidget(self.spinBox_ps)


        self.verticalLayout_12.addLayout(self.horizontalLayout_6)

        self.label_7 = QLabel(self.tab_set)
        self.label_7.setObjectName(u"label_7")

        self.verticalLayout_12.addWidget(self.label_7)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_5 = QLabel(self.tab_set)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_5.addWidget(self.label_5)

        self.spinBox_pw = QSpinBox(self.tab_set)
        self.spinBox_pw.setObjectName(u"spinBox_pw")
        self.spinBox_pw.setMaximum(1000)

        self.horizontalLayout_5.addWidget(self.spinBox_pw)


        self.verticalLayout_12.addLayout(self.horizontalLayout_5)

        self.label_8 = QLabel(self.tab_set)
        self.label_8.setObjectName(u"label_8")

        self.verticalLayout_12.addWidget(self.label_8)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_12.addItem(self.verticalSpacer_3)

        self.tabWidget.addTab(self.tab_set, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, 5, -1, -1)
        self.pushButtonSend = QPushButton(Dialog)
        self.pushButtonSend.setObjectName(u"pushButtonSend")
        self.pushButtonSend.setFocusPolicy(Qt.NoFocus)

        self.horizontalLayout_2.addWidget(self.pushButtonSend)

        self.pushButtonStop = QPushButton(Dialog)
        self.pushButtonStop.setObjectName(u"pushButtonStop")
        self.pushButtonStop.setFocusPolicy(Qt.NoFocus)

        self.horizontalLayout_2.addWidget(self.pushButtonStop)


        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)


        self.retranslateUi(Dialog)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Paste board", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), QCoreApplication.translate("Dialog", u"T1", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("Dialog", u"T2", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("Dialog", u"T3", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("Dialog", u"T4", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), QCoreApplication.translate("Dialog", u"T5", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_6), QCoreApplication.translate("Dialog", u"T6", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_7), QCoreApplication.translate("Dialog", u"T7", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_8), QCoreApplication.translate("Dialog", u"T8", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_9), QCoreApplication.translate("Dialog", u"T9", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p><span style=\" font-weight:700;\">This magic can only be used in Linux Terminal</span></p><p>1. Open a terminal, chdir(cd) to target dir</p><p>2. Keep focus on terminal, select a file on this page</p><p>3. Click send, wait and see the magic</p><p>4: Filename must be ascii, check MD5 after transfer</p></body></html>", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Target File:", None))
        self.labelFile.setText(QCoreApplication.translate("Dialog", u"N/A", None))
        self.pushButtonFile.setText(QCoreApplication.translate("Dialog", u"Select", None))
        self.checkBoxEcho.setText(QCoreApplication.translate("Dialog", u"Use \"echo\" only (2x Slower, but better compatibility)", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_f), QCoreApplication.translate("Dialog", u"File Transfer", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Click Interval / ms", None))
        self.label_9.setText(QCoreApplication.translate("Dialog", u"*Delay between two key inputs", None))
        self.label_6.setText(QCoreApplication.translate("Dialog", u"Packet Size / Bytes", None))
        self.label_7.setText(QCoreApplication.translate("Dialog", u"*Depends on Linux Terminal stdin size limitaion (1K~4K)", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", u"Packet Wait / ms", None))
        self.label_8.setText(QCoreApplication.translate("Dialog", u"*Delay between two commands for processing", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_set), QCoreApplication.translate("Dialog", u"Settings", None))
        self.pushButtonSend.setText(QCoreApplication.translate("Dialog", u"Send", None))
        self.pushButtonStop.setText(QCoreApplication.translate("Dialog", u"Stop", None))
    # retranslateUi


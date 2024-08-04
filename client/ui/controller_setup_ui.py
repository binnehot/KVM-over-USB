# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'controller_setup.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QHBoxLayout, QLabel, QLineEdit,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_ControllerSetupDialog(object):
    def setupUi(self, ControllerSetupDialog):
        if not ControllerSetupDialog.objectName():
            ControllerSetupDialog.setObjectName(u"ControllerSetupDialog")
        ControllerSetupDialog.resize(320, 240)
        self.verticalLayout = QVBoxLayout(ControllerSetupDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_com_select = QLabel(ControllerSetupDialog)
        self.label_com_select.setObjectName(u"label_com_select")

        self.horizontalLayout.addWidget(self.label_com_select)

        self.combobox_com_port = QComboBox(ControllerSetupDialog)
        self.combobox_com_port.setObjectName(u"combobox_com_port")

        self.horizontalLayout.addWidget(self.combobox_com_port)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_baud_rate = QLabel(ControllerSetupDialog)
        self.label_baud_rate.setObjectName(u"label_baud_rate")

        self.horizontalLayout_4.addWidget(self.label_baud_rate)

        self.line_edit_baud = QLineEdit(ControllerSetupDialog)
        self.line_edit_baud.setObjectName(u"line_edit_baud")

        self.horizontalLayout_4.addWidget(self.line_edit_baud)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_screen_x = QLabel(ControllerSetupDialog)
        self.label_screen_x.setObjectName(u"label_screen_x")

        self.horizontalLayout_2.addWidget(self.label_screen_x)

        self.line_edit_screen_x_size = QLineEdit(ControllerSetupDialog)
        self.line_edit_screen_x_size.setObjectName(u"line_edit_screen_x_size")

        self.horizontalLayout_2.addWidget(self.line_edit_screen_x_size)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_screen_y = QLabel(ControllerSetupDialog)
        self.label_screen_y.setObjectName(u"label_screen_y")

        self.horizontalLayout_3.addWidget(self.label_screen_y)

        self.line_edit_screen_y_size = QLineEdit(ControllerSetupDialog)
        self.line_edit_screen_y_size.setObjectName(u"line_edit_screen_y_size")

        self.horizontalLayout_3.addWidget(self.line_edit_screen_y_size)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.buttonBox = QDialogButtonBox(ControllerSetupDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(ControllerSetupDialog)
        self.buttonBox.accepted.connect(ControllerSetupDialog.accept)
        self.buttonBox.rejected.connect(ControllerSetupDialog.reject)

        QMetaObject.connectSlotsByName(ControllerSetupDialog)
    # setupUi

    def retranslateUi(self, ControllerSetupDialog):
        ControllerSetupDialog.setWindowTitle(QCoreApplication.translate("ControllerSetupDialog", u"Controller Setup", None))
        self.label_com_select.setText(QCoreApplication.translate("ControllerSetupDialog", u"Select COM port :", None))
        self.label_baud_rate.setText(QCoreApplication.translate("ControllerSetupDialog", u"Baud :", None))
        self.label_screen_x.setText(QCoreApplication.translate("ControllerSetupDialog", u"Screen size X :", None))
        self.line_edit_screen_x_size.setText(QCoreApplication.translate("ControllerSetupDialog", u"1920", None))
        self.label_screen_y.setText(QCoreApplication.translate("ControllerSetupDialog", u"Screen size Y :", None))
        self.line_edit_screen_y_size.setText(QCoreApplication.translate("ControllerSetupDialog", u"1080", None))
    # retranslateUi


# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'device_setup_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.5.2
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QFormLayout, QLabel,
    QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.setWindowModality(Qt.NonModal)
        Dialog.resize(279, 259)
        Dialog.setMaximumSize(QSize(16777215, 300))
        Dialog.setLayoutDirection(Qt.LeftToRight)
        self.formLayout = QFormLayout(Dialog)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label)

        self.comboBox = QComboBox(Dialog)
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setMouseTracking(False)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.comboBox)

        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_2)

        self.comboBox_2 = QComboBox(Dialog)
        self.comboBox_2.setObjectName(u"comboBox_2")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.comboBox_2)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.formLayout.setWidget(10, QFormLayout.FieldRole, self.buttonBox)

        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_3)

        self.comboBox_3 = QComboBox(Dialog)
        self.comboBox_3.setObjectName(u"comboBox_3")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.comboBox_3)

        self.checkBoxAudio = QCheckBox(Dialog)
        self.checkBoxAudio.setObjectName(u"checkBoxAudio")

        self.formLayout.setWidget(9, QFormLayout.FieldRole, self.checkBoxAudio)

        self.label_4 = QLabel(Dialog)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.label_4)

        self.comboBox_4 = QComboBox(Dialog)
        self.comboBox_4.setObjectName(u"comboBox_4")
        self.comboBox_4.setMouseTracking(False)

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.comboBox_4)

        self.label_5 = QLabel(Dialog)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.label_5)

        self.checkBoxAutoConnect = QCheckBox(Dialog)
        self.checkBoxAutoConnect.setObjectName(u"checkBoxAutoConnect")

        self.formLayout.setWidget(8, QFormLayout.FieldRole, self.checkBoxAutoConnect)

        self.comboBox_5 = QComboBox(Dialog)
        self.comboBox_5.setObjectName(u"comboBox_5")
        self.comboBox_5.setMouseTracking(False)

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.comboBox_5)

        self.label_7 = QLabel(Dialog)
        self.label_7.setObjectName(u"label_7")

        self.formLayout.setWidget(7, QFormLayout.SpanningRole, self.label_7)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Device setup", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"Device", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Resolution", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Format", None))
        self.checkBoxAudio.setText(QCoreApplication.translate("Dialog", u"Audio support", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"Audio IN", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", u"Audio OUT", None))
        self.checkBoxAutoConnect.setText(QCoreApplication.translate("Dialog", u"Auto Connect on startup", None))
        self.label_7.setText(QCoreApplication.translate("Dialog", u"* Audio routing only work in video recording", None))
    # retranslateUi


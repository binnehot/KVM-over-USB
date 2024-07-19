# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'indicator.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
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
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QHBoxLayout,
    QPushButton, QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.setWindowModality(Qt.WindowModal)
        Dialog.resize(400, 45)
        Dialog.setMinimumSize(QSize(400, 45))
        Dialog.setMaximumSize(QSize(400, 45))
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.pushButtonNum = QPushButton(Dialog)
        self.pushButtonNum.setObjectName(u"pushButtonNum")
        self.pushButtonNum.setFocusPolicy(Qt.NoFocus)

        self.horizontalLayout.addWidget(self.pushButtonNum)

        self.pushButtonCaps = QPushButton(Dialog)
        self.pushButtonCaps.setObjectName(u"pushButtonCaps")
        self.pushButtonCaps.setFocusPolicy(Qt.NoFocus)

        self.horizontalLayout.addWidget(self.pushButtonCaps)

        self.pushButtonScroll = QPushButton(Dialog)
        self.pushButtonScroll.setObjectName(u"pushButtonScroll")
        self.pushButtonScroll.setFocusPolicy(Qt.NoFocus)

        self.horizontalLayout.addWidget(self.pushButtonScroll)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Indicator Lights", None))
        self.pushButtonNum.setText(QCoreApplication.translate("Dialog", u"Num Lock", None))
        self.pushButtonCaps.setText(QCoreApplication.translate("Dialog", u"Caps Lock", None))
        self.pushButtonScroll.setText(QCoreApplication.translate("Dialog", u"Scroll Lock", None))
    # retranslateUi


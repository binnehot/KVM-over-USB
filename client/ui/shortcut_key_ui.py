# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'shortcut_key.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QGridLayout, QHBoxLayout,
    QKeySequenceEdit, QPushButton, QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.setWindowModality(Qt.WindowModal)
        Dialog.resize(400, 145)
        Dialog.setMinimumSize(QSize(400, 145))
        Dialog.setMaximumSize(QSize(400, 145))
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.pushButton_ctrl = QPushButton(Dialog)
        self.pushButton_ctrl.setObjectName(u"pushButton_ctrl")
        self.pushButton_ctrl.setFocusPolicy(Qt.NoFocus)
        self.pushButton_ctrl.setCheckable(True)
        self.pushButton_ctrl.setChecked(False)
        self.pushButton_ctrl.setAutoDefault(False)
        self.pushButton_ctrl.setFlat(False)

        self.gridLayout.addWidget(self.pushButton_ctrl, 0, 0, 1, 1)

        self.keySequenceEdit = QKeySequenceEdit(Dialog)
        self.keySequenceEdit.setObjectName(u"keySequenceEdit")

        self.gridLayout.addWidget(self.keySequenceEdit, 3, 0, 1, 3)

        self.pushButton_shift = QPushButton(Dialog)
        self.pushButton_shift.setObjectName(u"pushButton_shift")
        self.pushButton_shift.setFocusPolicy(Qt.NoFocus)
        self.pushButton_shift.setCheckable(True)
        self.pushButton_shift.setAutoDefault(False)

        self.gridLayout.addWidget(self.pushButton_shift, 0, 1, 1, 1)

        self.pushButton_alt = QPushButton(Dialog)
        self.pushButton_alt.setObjectName(u"pushButton_alt")
        self.pushButton_alt.setFocusPolicy(Qt.NoFocus)
        self.pushButton_alt.setCheckable(True)
        self.pushButton_alt.setAutoDefault(False)

        self.gridLayout.addWidget(self.pushButton_alt, 0, 2, 1, 1)

        self.pushButton_tab = QPushButton(Dialog)
        self.pushButton_tab.setObjectName(u"pushButton_tab")
        self.pushButton_tab.setFocusPolicy(Qt.NoFocus)
        self.pushButton_tab.setCheckable(True)
        self.pushButton_tab.setAutoDefault(False)

        self.gridLayout.addWidget(self.pushButton_tab, 2, 0, 1, 1)

        self.pushButton_prtsc = QPushButton(Dialog)
        self.pushButton_prtsc.setObjectName(u"pushButton_prtsc")
        self.pushButton_prtsc.setFocusPolicy(Qt.NoFocus)
        self.pushButton_prtsc.setCheckable(True)
        self.pushButton_prtsc.setAutoDefault(False)

        self.gridLayout.addWidget(self.pushButton_prtsc, 2, 1, 1, 1)

        self.pushButton_clear = QPushButton(Dialog)
        self.pushButton_clear.setObjectName(u"pushButton_clear")
        self.pushButton_clear.setFocusPolicy(Qt.StrongFocus)

        self.gridLayout.addWidget(self.pushButton_clear, 3, 3, 1, 1)

        self.pushButton_meta = QPushButton(Dialog)
        self.pushButton_meta.setObjectName(u"pushButton_meta")
        self.pushButton_meta.setFocusPolicy(Qt.NoFocus)
        self.pushButton_meta.setCheckable(True)
        self.pushButton_meta.setAutoDefault(False)

        self.gridLayout.addWidget(self.pushButton_meta, 0, 3, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, 5, -1, -1)
        self.pushButtonSend = QPushButton(Dialog)
        self.pushButtonSend.setObjectName(u"pushButtonSend")
        self.pushButtonSend.setFocusPolicy(Qt.NoFocus)

        self.horizontalLayout_2.addWidget(self.pushButtonSend)

        self.pushButtonSave = QPushButton(Dialog)
        self.pushButtonSave.setObjectName(u"pushButtonSave")
        self.pushButtonSave.setFocusPolicy(Qt.NoFocus)

        self.horizontalLayout_2.addWidget(self.pushButtonSave)


        self.gridLayout.addLayout(self.horizontalLayout_2, 4, 0, 1, 4)

        QWidget.setTabOrder(self.pushButton_ctrl, self.pushButton_shift)
        QWidget.setTabOrder(self.pushButton_shift, self.pushButton_alt)
        QWidget.setTabOrder(self.pushButton_alt, self.pushButton_meta)
        QWidget.setTabOrder(self.pushButton_meta, self.pushButton_tab)
        QWidget.setTabOrder(self.pushButton_tab, self.pushButton_prtsc)
        QWidget.setTabOrder(self.pushButton_prtsc, self.keySequenceEdit)
        QWidget.setTabOrder(self.keySequenceEdit, self.pushButton_clear)

        self.retranslateUi(Dialog)

        self.pushButton_ctrl.setDefault(False)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Custom Key", None))
        self.pushButton_ctrl.setText(QCoreApplication.translate("Dialog", u"Ctrl", None))
        self.pushButton_shift.setText(QCoreApplication.translate("Dialog", u"Shift", None))
        self.pushButton_alt.setText(QCoreApplication.translate("Dialog", u"Alt", None))
        self.pushButton_tab.setText(QCoreApplication.translate("Dialog", u"Tab", None))
        self.pushButton_prtsc.setText(QCoreApplication.translate("Dialog", u"Prt Sc", None))
#if QT_CONFIG(tooltip)
        self.pushButton_clear.setToolTip(QCoreApplication.translate("Dialog", u"Clear Selection", None))
#endif // QT_CONFIG(tooltip)
        self.pushButton_clear.setText(QCoreApplication.translate("Dialog", u"Clear", None))
        self.pushButton_meta.setText(QCoreApplication.translate("Dialog", u"Meta", None))
        self.pushButtonSend.setText(QCoreApplication.translate("Dialog", u"Send", None))
        self.pushButtonSave.setText(QCoreApplication.translate("Dialog", u"Save", None))
    # retranslateUi


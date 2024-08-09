# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'about.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
    QSizePolicy, QTextEdit, QVBoxLayout, QWidget)

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        if not AboutDialog.objectName():
            AboutDialog.setObjectName(u"AboutDialog")
        AboutDialog.resize(507, 325)
        self.verticalLayout = QVBoxLayout(AboutDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout_0 = QVBoxLayout()
        self.verticalLayout_0.setObjectName(u"verticalLayout_0")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_project_name_key = QLabel(AboutDialog)
        self.label_project_name_key.setObjectName(u"label_project_name_key")

        self.horizontalLayout.addWidget(self.label_project_name_key)

        self.label_project_name_value = QLabel(AboutDialog)
        self.label_project_name_value.setObjectName(u"label_project_name_value")
        self.label_project_name_value.setText(u"<a href=\"https://github.com/binnehot/KVM-over-USB\">KVM-over-USB</a>")
        self.label_project_name_value.setWordWrap(False)
        self.label_project_name_value.setOpenExternalLinks(True)

        self.horizontalLayout.addWidget(self.label_project_name_value)


        self.verticalLayout_0.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_project_description_value = QLabel(AboutDialog)
        self.label_project_description_value.setObjectName(u"label_project_description_value")

        self.horizontalLayout_2.addWidget(self.label_project_description_value)

        self.label_project_description_key = QLabel(AboutDialog)
        self.label_project_description_key.setObjectName(u"label_project_description_key")

        self.horizontalLayout_2.addWidget(self.label_project_description_key)


        self.verticalLayout_0.addLayout(self.horizontalLayout_2)


        self.verticalLayout.addLayout(self.verticalLayout_0)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_fork_from_key = QLabel(AboutDialog)
        self.label_fork_from_key.setObjectName(u"label_fork_from_key")

        self.horizontalLayout_3.addWidget(self.label_fork_from_key)

        self.label_fork_from_value = QLabel(AboutDialog)
        self.label_fork_from_value.setObjectName(u"label_fork_from_value")
        self.label_fork_from_value.setText(u"<a href=\"https://github.com/ElluIFX/KVM-Card-Mini-PySide6\">ElluIFX: KVM-Card-Mini-PySide6</a>")
        self.label_fork_from_value.setOpenExternalLinks(True)

        self.horizontalLayout_3.addWidget(self.label_fork_from_value)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.label_build_info = QLabel(AboutDialog)
        self.label_build_info.setObjectName(u"label_build_info")

        self.verticalLayout.addWidget(self.label_build_info)

        self.text_edit_info = QTextEdit(AboutDialog)
        self.text_edit_info.setObjectName(u"text_edit_info")
        self.text_edit_info.setReadOnly(True)

        self.verticalLayout.addWidget(self.text_edit_info)


        self.retranslateUi(AboutDialog)

        QMetaObject.connectSlotsByName(AboutDialog)
    # setupUi

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QCoreApplication.translate("AboutDialog", u"About", None))
        self.label_project_name_key.setText(QCoreApplication.translate("AboutDialog", u"Project name:", None))
        self.label_project_description_value.setText(QCoreApplication.translate("AboutDialog", u"Project description:", None))
        self.label_project_description_key.setText(QCoreApplication.translate("AboutDialog", u"A simple KVM client", None))
        self.label_fork_from_key.setText(QCoreApplication.translate("AboutDialog", u"Fork from:", None))
        self.label_build_info.setText(QCoreApplication.translate("AboutDialog", u"Build info:", None))
    # retranslateUi


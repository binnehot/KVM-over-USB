pyside6-lupdate.exe .\main.py .\ui\main.ui .\ui\device_setup_dialog.ui .\ui\indicator.ui .\ui\numboard.ui .\ui\paste_board.ui .\ui\shortcut_key.ui .\ui\controller_setup.ui -ts .\translate\trans_cn.ts

pyside6-linguist .\translate\trans_cn.ts

pyside6-lrelease .\translate\trans_cn.ts -qm .\translate\trans_cn.qm

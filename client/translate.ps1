pyside6-lupdate.exe .\main.py .\ui\main.ui .\ui\device_setup_dialog.ui .\ui\indicator.ui .\ui\numboard.ui .\ui\paste_board.ui .\ui\shortcut_key.ui -ts trans_cn.ts

pyside6-linguist .\trans_cn.ts

pyside6-lrelease .\trans_cn.ts -qm .\trans_cn.qm

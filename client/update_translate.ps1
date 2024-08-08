pyside6-lupdate.exe .\main.py -recursive .\ui -ts .\translate\trans_zh_cn.ts -no-obsolete

pyside6-linguist .\translate\trans_zh_cn.ts

pyside6-lrelease .\translate\trans_zh_cn.ts -qm .\translate\trans_zh_cn.qm

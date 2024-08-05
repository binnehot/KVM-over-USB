python.exe -m nuitka --windows-console-mode=disable --show-progress --standalone --enable-plugin=pyside6 --output-dir=build_console --windows-icon-from-ico=.\icons\icon.ico --jobs=16 .\Mini-KVM.py --include-data-dir=.\icons=icons --include-data-dir=.\web=web --include-data-dir=.\web_s=web_s --include-data-dir=.\data=data --include-data-dir=.\translate=translate --onefile-windows-splash-screen-image=booting.png --include-qt-plugins=multimedia --onefile --quiet --noinclude-qt-translations --noinclude-dlls=libQt6Charts* --noinclude-dlls=libQt6Quick3D* --noinclude-dlls=libQt6Sensors* --noinclude-dlls=libQt6Test* --noinclude-dlls=libQt6WebEngine* --noinclude-dlls=qt6web* --noinclude-dlls=qt6pdf*

Move-Item -Path .\build_console\Mini-KVM.exe -Destination .\Mini-KVM-Client\Mini-KVM.exe -Force

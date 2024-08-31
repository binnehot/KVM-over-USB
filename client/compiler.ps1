pip freeze > requirements.txt
python.exe -m nuitka --show-progress --standalone --python-flag=-u --enable-plugin=pyside6 --output-dir=build --windows-console-mode=disable --product-name="usb kvm client" --windows-file-description="A simple USB KVM client" --windows-product-version="1.0.0.0" --windows-icon-from-ico=.\icons\icon.ico --onefile-windows-splash-screen-image=.\icons\splash.png --jobs=16 .\usb_kvm_client.py --include-data-dir=.\icons=icons --include-data-dir=.\data=data --include-data-dir=.\translate=translate --include-qt-plugins=multimedia --onefile --quiet --noinclude-qt-translations --noinclude-dlls=libQt6Charts* --noinclude-dlls=libQt6Quick3D* --noinclude-dlls=libQt6Sensors* --noinclude-dlls=libQt6Test* --noinclude-dlls=libQt6WebEngine* --noinclude-dlls=qt6web* --noinclude-dlls=qt6pdf*

New-Item -Name "releases" -ItemType "directory" -Force
Move-Item -Path .\build\usb_kvm_client.exe -Destination .\releases\usb_kvm_client.exe -Force

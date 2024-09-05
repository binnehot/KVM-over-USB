# KVM over USB
A simple KVM USB solution


## Synopsis
When a server loses network connectivity, it can be difficult to get back to work. Although there are technologies like IPMI that can help us to solve the problem, often such devices are expensive.
For home users, this project helps you to quickly manage/maintain your server using other PCs/laptops connected via USB.


## Hardware
For most users, it is difficult to ask users to manufacture their own PCB.
A non-profit project that involves commissioning a manufacturer is obviously also difficult.
So this project recommends using a combination of products already available on the market.


### Hardware list
1. Video capture card: You can use video capture cards with chips such as MS2109 or MS2130, which are sold in the market for about 5-15 USD.
2. CH340 to CH9329 USB Connection Cable: CH340 is a common USB to serial chip, access CH9329 through the serial port, and finally connect CH9329 to the controlled device can be.
Note 1: There are finished cables available on shopping platforms, which can be purchased directly at a market price of about 20 RMB.
Note 2: If you have special needs, you can also purchase a USB to serial cable with other chips (e.g. FT232) and then purchase a CH9329 module with a serial interface.
3. HDMI cable
4. If the device does not have enough USB ports, it is recommended to use it with a USB HUB.


### Schematic
![image](https://github.com/wevsty/KVM-over-USB/blob/main/document/connection_schematic.svg)

### Hardware photos
![image](https://github.com/wevsty/KVM-over-USB/blob/main/document/hardware_photos.jpg)

## 软件
The software client of the project is based on the source code of [KVM-Card-Mini-PySide6](https://github.com/ElluIFX/KVM-Card-Mini-PySide6) with modifications, and adapts CH9329 for keyboard and mouse input.


### Client build

Assuming you have git, python, and poetry installed, you can run the following commands to compile.
```powershell
git clone https://github.com/wevsty/KVM-over-USB.git
cd client
poetry shell
poetry install
./compiler.ps1
```


### Client download

Please visit the releases page to download the compiled client.
Note: Currently the client (console) is only supported for Windows.

https://github.com/wevsty/KVM-over-USB/releases


### 使用方法

1. If you are using the CH340 USB to serial chip, you may need to install the CH340 driver first.

CH340 driver download address: https://www.wch.cn/downloads/CH341SER_EXE.html
After successful installation, you can check the serial port number through the device manager.

![image](https://github.com/wevsty/KVM-over-USB/blob/main/document/device_manager_port.png)
Note: The port number may be randomized and not fixed.

2. Execute usb_kvm_client

Video Connection:

Select Device menu -> Video Device -> Select the correct video capture card -> OK.

![image](https://github.com/wevsty/KVM-over-USB/blob/main/document/video_device_setup.png)

Controller Connection:
In most cases, the default configuration will automatically select the serial port, but if you have more than one serial port on your device, you may need to manually select the serial port name.

Select Device Menu -> Controller Settings -> Select the correct serial port -> OK.

![image](https://github.com/wevsty/KVM-over-USB/blob/main/document/controller_device_setup.png)

### Demo

Demo control ASUS BIOS
![image](https://github.com/wevsty/KVM-over-USB/blob/main/document/demo_control_bios.gif)

### FAQ

Q: Why doesn't the mouse work when the console is Linux?
A: Some operating systems do not support absolute coordinate mode, please try to switch to relative coordinate mode.

Q: How do I send the Ctrl + Alt + Delete key combination?
A: Due to the Windows mechanism it is difficult to intercept these key combinations. To send these combinations to the console, use the shortcut function in the keyboard menu.

## Thanks

[Jackadminx](https://github.com/Jackadminx)/[KVM-Card-Mini](https://github.com/Jackadminx/KVM-Card-Mini)

[ElluIFX](https://github.com/ElluIFX)/[KVM-Card-Mini-PySide6](https://github.com/ElluIFX/KVM-Card-Mini-PySide6)

[binnehot](https://github.com/binnehot)/[KVM-over-USB](https://github.com/binnehot/KVM-over-USB)

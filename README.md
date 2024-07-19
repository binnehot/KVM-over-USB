# KVM over USB (改)
一个简单的KVM over USB方案

## 简介
这个项目是沿着这两位老哥走的路，整合出了一个 【便宜】+【又不是不能用】的 **KVM over USB (改)**  方案。

[Jackadminx](https://github.com/Jackadminx)/[KVM-Card-Mini](https://github.com/Jackadminx/KVM-Card-Mini)

[ElluIFX](https://github.com/ElluIFX)/[KVM-Card-Mini-PySide6](https://github.com/ElluIFX/KVM-Card-Mini-PySide6)

## 硬件
三/四个常规小配件，不用做PCB板，花70+块钱就能搭出这个KVM over USB的方案。

1. 视频采集卡：理论上所有MS2130采集卡都可以  (40-90+元）
2. CH9329虚拟键盘鼠标usb线：这是采用CH340+CH9329方案的usb转COM，再转USB模拟HID的线  (20元+）
3. HDMI线：1080P分辨率，没有特别要求  (10元+）
4. （usb3.0集线器）：如果电脑有两个usb口，可以省略。如果用usb2.0的集线器，也行。


【硬件图】
![image](https://github.com/binnehot/KVM-over-USB/blob/main/image/0_HW_KVM_photo.JPG)


【硬件框图】
![image](https://github.com/binnehot/KVM-over-USB/blob/main/image/1_HW_drawing.png)


## 软件
由于硬件改变，软件需要适配。
视频采集卡，即插即用，不用改东西。虚拟键鼠usb线，芯片方案都改了，原来的hid_def.py重新写了一遍，还有一个键盘码文件keyboard_ch9329code2Key.yaml。ch9329的python库可以直接pip安装。

## 编译
需要的文件

- 原项目ElluFX/KVM 项目v1.1的client文件夹
- ./Client/hid_def.py 覆盖原文件
- ./Client/data/HIDcode2KeyName.yaml 增加这个文件

_注意原项目有个文件夹名字需要确认一下，”./Client/data“中的”data“全部小写。_

requirements
参考原项目requirements.txt，再多三个库 numpy, pyserial 和 ch9329

## 使用

Windows客户端（控制端）
（不想自己编译，就下载这个KVMoverUSB.exe文件）
1，第一次使用可能需要安装CH340的驱动。 参照官方说明安装。 
[官网驱动安装指导视频](https://www.wch.cn/videos/ch340.html)
如果安装成功可以在 … 中看到 COM口号码

【设别管理器 COM端口号】

![image](https://github.com/binnehot/KVM-over-USB/blob/main/image/2_COM_port.png)


2，配置COM端口。
默认端口COM9，如果需要更改端口，请在HID setting对话框更改， 或者编辑文件 config_hid.yaml

【HID setting】

![image](https://github.com/binnehot/KVM-over-USB/blob/main/image/3_COM_setting.png)


服务端（被控制端）
HDMI和USB，即插即用，不用安装驱动，不挑操作系统，BIOS设置也支持。
注意：UI中 原项目留下来的某些功能需要原硬件支持，放在这里就没用了，比如，RGB灯，MCU重置…

【应用例子，修改BIOS设定】

![image](https://github.com/binnehot/KVM-over-USB/blob/main/image/4_BIOS_Gif.gif)

### 已知问题

1.  键盘打字快了会出现重复字符，可以试一试用一个手指头打字，慢一点，或者等原作者优化原来的项目
2.  鼠标移动和点击有点慢，需要练习和技巧，这也需要原作者优化原来的项目，或者接一个无线鼠标


## 感谢
特别感谢 [ElluIFX](https://github.com/ElluIFX)，如果有时间的话，期待键盘打字优化一轮，再次感谢。 

# config.py
# 功能：集中存放项目配置参数
# 好处：以后从 Windows 移植到 Jetson 时，优先只改这里，不乱改主程序

# 摄像头编号
# Windows 上 USB 摄像头通常是 0
# 到 Jetson 上如果打不开，可以改成 1、2 试试
CAMERA_INDEX = 1

# OpenCV 显示窗口的名字
WINDOW_NAME = "USB Camera"
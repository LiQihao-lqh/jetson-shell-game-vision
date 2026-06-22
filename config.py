# config.py
# 功能：集中存放项目配置参数
# 好处：以后从 Windows 移植到 Jetson 时，优先只改这里，不乱改主程序

# 摄像头编号
# Windows 上 USB 摄像头通常是 0
# 到 Jetson 上如果打不开，可以改成 1、2 试试
CAMERA_INDEX = 1

SERVO_PORT = "COM4"
SERVO_BAUDRATE = 115200

#自己设置摄像头分辨率
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# 目标颜色的 HSV 下限
LOWER_COLOR = (0, 43, 46)

#红色比较特殊，它在 HSV 色环两端：
#0 ~ 10       一段红色
#170 ~ 179    另一段红色
#所以要写两个上下限，对应两个mask，最后合并
# 目标颜色的 HSV 上限
UPPER_RED1 = (10, 255, 255)
UPPER_RED2 = (179, 255, 255)

# 最小目标面积，小于这个面积就认为是噪声
LOWER_RED1 = (0, 43, 46)
LOWER_RED2 = (170, 43, 46)

# 最小目标面积，小于这个面积就认为是噪声
# 最大目标面积，大于这个面积就认为是噪声
MIN_TARGET_AREA = 500
MAX_TARGET_AREA = 50000
# OpenCV 显示窗口的名字
WINDOW_NAME = "USB Camera"

# 目标的宽高比，小于这个值就认为是噪声
MIN_ASPECT_RATIO = 0.5
# 目标的宽高比，大于这个值就认为是噪声
MAX_ASPECT_RATIO = 2.0

# 形态学卷积核的大小
MORPH_KERNEL_SIZE = 5

#yolo模型选择
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

MODEL_PATH = PROJECT_ROOT / "models" / "trained" / "card_seg_v4" / "weights" / "best.pt"

YOLO_CONF = 0.4
YOLO_DEVICE = 0

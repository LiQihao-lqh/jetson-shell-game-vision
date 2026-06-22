# vision_detector.py
# 功能：
# 1. 接收 main.py 传入的一帧画面 frame
# 2. 对画面进行红色目标识别
# 3. 筛选有效目标轮廓
# 4. 返回目标中心点、外接矩形、面积和宽高比等信息
#
# 说明：
# 这个文件不再负责打开摄像头、显示窗口、计算 FPS、按 q 退出。
# 这些主流程工作交给 main.py 负责。


import cv2

#类似#include "config.h"的作用，导入配置参数
import numpy as np
from ultralytics import YOLO

from config import (
    MODEL_PATH,
    YOLO_CONF,
    YOLO_DEVICE,
)

model = YOLO(str(MODEL_PATH))

#这个文件是视觉识别算法模块，负责从一帧画面中识别目标，并输出目标信息。
def detect_target(frame):
    result = model.predict(
        source=frame,
        conf=YOLO_CONF,
        device=YOLO_DEVICE,
        verbose=False,
    )[0]

    if result.boxes is None or len(result.boxes) == 0:
        empty_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        return False, None, empty_mask

    best_index = int(result.boxes.conf.argmax().item())

    x1, y1, x2, y2 = result.boxes.xyxy[best_index].cpu().numpy()
    conf = float(result.boxes.conf[best_index].cpu().numpy())
    class_id = int(result.boxes.cls[best_index].cpu().numpy())
    class_name = result.names[class_id]

    x = int(x1)
    y = int(y1)
    w = int(x2 - x1)
    h = int(y2 - y1)

    cx = x + w // 2
    cy = y + h // 2

    area = w * h
    aspect_ratio = w / h if h != 0 else 0

    if result.masks is not None:
        mask = result.masks.data[best_index].cpu().numpy()
        mask = (mask * 255).astype(np.uint8)
        mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))
    else:
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)

    target_info = {
        "x": x,
        "y": y,
        "w": w,
        "h": h,
        "cx": cx,
        "cy": cy,
        "area": area,
        "aspect_ratio": aspect_ratio,
        "conf": conf,
        "class_id": class_id,
        "class_name": class_name,
    }

    return True, target_info, mask


def draw_target(frame, target):
    
    #先把数据取出来这样后面就不用写 target["x"]
    #从 target 这个字典里，取出名字叫 "x" 的数据
    x = target["x"]
    y = target["y"]
    w = target["w"]
    h = target["h"]
    cx = target["cx"]
    cy = target["cy"]
    area = target["area"]
    aspect_ratio = target["aspect_ratio"]

    # 在原图上画出目标矩形框,颜色是绿色，线宽是2
    #这样就能看到目标被一个绿色的矩形框住了
    #(x, y), (x + w, y + h)是矩形框的左上角和右下角坐标
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # 在目标中心点画一个圆点
    #(cx, cy), 5, 圆心坐标，半径
    cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

    #创建一个文本字符串，用于显示目标中心坐标
    #f-“string”格式化字符串，{cx}和{cy}会被替换成实际的坐标值
    # 在画面上显示目标中心坐标
    # (x, y - 10)是文本位置，稍微高于矩形框
    #FONT_HERSHEY_SIMPLEX,opencv提供的一种字体
    cv2.putText(
        frame,
        # 显示目标中心坐标、面积和宽高比在画面上
        #0f 表示保留0位小数,2f 表示保留2位小数
        f"center: ({cx}, {cy}), area: {area:.0f} ratio: {aspect_ratio:.2f}",
        (x, y - 10),
        #x是矩形框的左上角坐标，y是矩形框的左上角坐标减去10，实现稍微高于矩形框的效果
        # 设置字体类型和特征，字体大小为0.6，颜色为绿色，线宽为2
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2
    )

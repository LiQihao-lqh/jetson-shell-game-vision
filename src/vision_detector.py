# vision_detector.py
# 功能：
# 两个函数：
# 1. detect_target(frame): 从一帧画面中识别目标，并输出目标信息。
# 2. draw_target(frame, target): 把目标信息画在原图上。
#
# 说明：
# 这个文件不再负责打开摄像头、显示窗口、计算 FPS、按 q 退出。
# 这些主流程工作交给 main.py 负责。


import cv2
# 导入 numpy 库，用于数组操作
import numpy as np
# 导入 ultralytics 库，的yolo模型
from ultralytics import YOLO

#导入
# 模型路径
# 置信度
# 设备型号参数
from config import (
    MODEL_PATH,
    YOLO_CONF,
    YOLO_DEVICE,
)

#str()转换路径
#加载模型
model = YOLO(str(MODEL_PATH))

#视觉识别算法，从一帧画面中识别目标，并输出目标信息。
def detect_target(frame):
    result = model.predict(
        source=frame,
        conf=YOLO_CONF,
        #这里是设备型号，指我的显卡
        device=YOLO_DEVICE,
        # 是否在终端打印识别结果，一堆参数
        verbose=False,
    )[0]
#取第0个结果，也就是最前面那个，因为只有一帧画面，所以只有1个结果

    if result.boxes is None or len(result.boxes) == 0:
        #没识别到就创建一个空的mask
        empty_mask = np.zeros(frame.shape[:2], dtype=np.uint8)

        #和c语言的return一个意思，main里面调用会返回三个值
        #False表示没有识别到目标
        #None表示没有目标信息
        #empty_mask表示空的mask
        return False, None, empty_mask

    #从所有检测结果里选置信度最高的那个目标
    #argmax()函数返回数组中最大值的索引
    #返回数组或张量中最大值所在的索引（位置），而不是最大值本身
    #item()函数将张量转换为Python标量
    #注：这里是张量
    best_index = int(result.boxes.conf.argmax().item())

    #取矩形框的左上角和右下角的坐标，
    #cpu()把数据从显卡拿到CPU，方便后续操作
    #注：numpy这里是向量数组
    x1, y1, x2, y2 = result.boxes.xyxy[best_index].cpu().numpy()
    conf = float(result.boxes.conf[best_index].cpu().numpy())
    #cls[]是目标的类别
    class_id = int(result.boxes.cls[best_index].cpu().numpy())
    class_name = result.names[class_id]

    #把原始坐标转化为我自己的坐标系，然后整数化
    x = int(x1)
    y = int(y1)
    w = int(x2 - x1)
    h = int(y2 - y1)

    #算目标中心点，// 是整除向下取整
    cx = x + w // 2
    cy = y + h // 2

    #算目标面积和宽高比
    #显示调试信息
    #判断目标远近的大概变化
    #后面可以辅助过滤异常目标
    area = w * h
    aspect_ratio = w / h if h != 0 else 0

    #判断yolo是否输出了mask
    if result.masks is not None:
        #从yolo的结果里取目标的mask，然后把数据从显卡拿到CPU，方便后续操作
        mask = result.masks.data[best_index].cpu().numpy()
        #把mask是0-1的值映射到0-255，astype(np.uint8)转换成 OpenCV 常用的 8 位图像格式。
        mask = (mask * 255).astype(np.uint8)
        #把mask的大小调整为和原图相同，opencv的顺序是width, height，而mask的顺序是height, width
        mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))
    else:
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)

    #把数据打包到字典里面
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

#负责把目标信息画在原图上
def draw_target(frame, target):
    
    #先把数据取出来这样后面就不用写 target["x"]
    #一次性把数据取好，方便后面使用
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

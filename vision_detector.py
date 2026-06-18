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
from config import (
    LOWER_RED1,
    UPPER_RED1,
    LOWER_RED2,
    UPPER_RED2,
    MIN_TARGET_AREA,
    MAX_TARGET_AREA,
    MIN_ASPECT_RATIO,
    MAX_ASPECT_RATIO,
    MORPH_KERNEL_SIZE,
)


#这个文件是视觉识别算法模块，负责从一帧画面中识别目标，并输出目标信息。
def detect_target(frame):
    
    #目标识别函数：
    #输入一帧画面 frame，识别红色目标。

    #返回：
    #found:
        #是否找到有效目标，True 表示找到，False 表示没找到。
    #target:
        #目标信息字典，里面包含 cx、cy、x、y、w、h、area、aspect_ratio。
        #如果没找到目标，target 为 None。
    

    #把读取到的画面从 BGR 颜色空间转换到 HSV 颜色空间
    #cvtcolor，意思是convert（转换）。转换看颜色的方式，BGR是OpenCV默认的颜色空间，HSV更适合做颜色分割
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    #根据设置的颜色范围，生成一个掩膜区域，区域内的为255（白色），区域外的为0（黑色）
    mask1 = cv2.inRange(hsv, LOWER_RED1, UPPER_RED1)
    mask2 = cv2.inRange(hsv, LOWER_RED2, UPPER_RED2)
    mask = mask1 + mask2

    #去掉整张图中的小噪点，保留核心区域
    #getStructuringElement获取结构元素，MORPH_RECT表示矩形结构，
    # (MORPH_KERNEL_SIZE, MORPH_KERNEL_SIZE)表示结构元素的大小
    #类似卷积核，RECT 是 rectangle，矩形。
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (MORPH_KERNEL_SIZE, MORPH_KERNEL_SIZE))

    # 这里是具体操作方法，开运算即：先腐蚀后膨胀
    # 去除噪点
    #morphologyEx：执行形态学操作，
    # mask：要处理的图，MORPH_OPEN：使用开运算，
    # kernel：用刚才那个 5x5 小刷子处理
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    #MORPH_CLOSE 闭运算即：先膨胀后腐蚀
    #作用是：填充小孔，连接断开的轮廓
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    #contours：轮廓,   _ 这里原本层级信息，但是不需要，所以用 _ 占位
    #findContours：寻找轮廓，
    # RETR：检索，EXTERNAL：外轮廓
    # CHAIN：轮廓点链 轮廓是很多的点连起来找到的
    # APPROX：approximate，近似 SIMPLE：简单
    # 总体意思：用简化近似的方式保留轮廓点
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #valid_contours：有效轮廓
    #[]表示一个空列表，用来存储有效轮廓
    #创建一个表格存可能的目标轮廓，然后再按照面积和宽高比，筛选出有效的目标
    valid_contours = []

    # 遍历所有轮廓
    #contour in contours :意思是：遍历 contours 列表中的每个元素，每个元素都是一个轮廓的点集
    for contour in contours:

        # 计算当前轮廓的面积
        area = cv2.contourArea(contour)

        #面积太大或者太小，判断为噪声
        if area < MIN_TARGET_AREA or area > MAX_TARGET_AREA:
            continue

        # 获取目标外接矩形的位置和大小
        # bounding：边界
        #boundingRect：计算轮廓的外接矩形
        #返回值是矩形的左上角坐标（x, y）和宽高（w, h）
        x, y, w, h = cv2.boundingRect(contour)

        # 防止计算宽高比时除以 0
        # 理论上 h 一般不会是 0，但写上更安全
        if h == 0:
            continue

        # 计算目标的宽高比
        aspect_ratio = w / h

        if aspect_ratio < MIN_ASPECT_RATIO or aspect_ratio > MAX_ASPECT_RATIO:
            continue

        # 在有效轮廓列表中添加当前轮廓
        # append() 意思是在列表末末添加一个元素
        #valid_contours 意思是有有效轮廓的列表
        #contour,x,y,w,h 把当前轮廓的点集、外接矩形的左上角坐标（x, y）和宽高（w, h）添加到有效轮廓列表中
        valid_contours.append((contour, area, x, y, w, h, aspect_ratio))

    #len(valid_contours) 表示有效轮廓列表的长度,len()函数返回列表的元素个数
    #如果有效轮廓列表的长度等于0，说明没有有效轮廓
    if len(valid_contours) == 0:
        return False, None, mask

    # 找到面积最大的有效轮廓
    #key=lambda item: item[1] 表示根据每个轮廓的面积来判断最大值
    #lambda item: item[1] 可以理解成一个临时小函数。
    #对于 valid_targets 里面的每一个 item，取 item[1] 作为比较依据
    #key是选定标准，这里是面积
    #lambda: 表示匿名函数， 匿名函数指的是没有名字的函数，在这里的作用是返回每个轮廓的面积（第2个元素）的值
    target = max(valid_contours, key=lambda item: item[1])

    #这里target是一个元组，作用是：记录数据，方便后续使用
    contour, area, x, y, w, h, aspect_ratio = target

    # 计算目标中心点坐标
    #cy是center y cx是center x
    #// 是整数除法，结果向下取整
    cx = x + w // 2
    cy = y + h // 2

    # 用字典（dictionary）保存目标信息，方便 main.py 和 gimbal_tracker.py 使用
    #info-information
    #"x": x，意思是 把变量 x 的值，存到字典里，名字叫 "x"
    target_info = {
        "contour": contour,
        "area": area,
        "x": x,
        "y": y,
        "w": w,
        "h": h,
        "aspect_ratio": aspect_ratio,
        "cx": cx,
        "cy": cy,
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

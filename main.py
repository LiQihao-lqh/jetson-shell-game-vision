# main.py
# 功能：
# 1. 打开 USB 摄像头
# 2. 实时读取摄像头画面
# 3. 用 OpenCV 显示画面
# 4. 按 q 退出程序
#
# 预期现象：
# 运行后弹出摄像头画面窗口，按 q 后关闭窗口并释放摄像头


#使用time模块计算帧率，获取当前时间
import time
import cv2

#类似#include "config.h"的作用，导入配置参数
from config import (
    CAMERA_INDEX,
    WINDOW_NAME,
    FRAME_WIDTH,
    FRAME_HEIGHT,
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

#这个文件是主程序，负责摄像头的打开、画面的读取和显示，以及资源的释放。
def main():
    """
    主函数：
    负责打开摄像头、循环读取画面、显示画面、退出后释放资源。
    """

    # 创建摄像头对象
    # CAMERA_INDEX 来自 config.py，方便以后移植到 Jetson 时修改
    #cap：句柄指的是摄像头这个对象
    #cap.read()意思是读取数据，cap.release()意思是释放资源
    #不走GStreamer，直接读取摄像头画面，强制走V4L2接口
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_V4L2)

    #设置视频编码格式为MJPG
    #MJPG：Motion JPEG，是一种压缩格式，用于网络传输
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

    #prop意思是property，属性的意思
    #
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)



    # 判断摄像头是否成功打开
    if not cap.isOpened():
        print("摄像头打开失败，请检查摄像头编号或连接状态")
        return

#变量 prev_time 表示：上一帧画面的时间
#time.time()表示：获取当前时间的时间戳
#意思是获取一个时间点，这个时间点可能是随机的

    prev_time = time.time()
    #就是while（1），知道按下q才退出循环
    while True:
        # 从摄像头读取一帧画面
        # ret 表示是否读取成功
        # frame 表示读取到的图像数据
        #读取成功ret=True，读取失败ret=False
        #读取成功就就执行cap.read()
        #执行 cap.read()，然后把结果拆成两个变量，ret 和 frame
        #ret表示状态，是一个布尔值，frame表示读取到的图像数据
        ret, frame = cap.read()
        # 如果读取失败，退出循环
        #不写if，else这样不用多包一层
        if not ret:
            print("画面读取失败")
            break

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
        #如果有效轮廓列表的长度大于0，说明有有效轮廓
        if len(valid_contours) > 0:
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
                cv2.putText(frame,
                            # 显示目标中心坐标、面积和宽高比在画面上
                            #0f 表示保留0位小数,2f 表示保留2位小数
                           f"center: ({cx}, {cy}), area: {area:.0f} ratio: {aspect_ratio:.2f}", (x, y - 10),
                           #x是矩形框的左上角坐标，y是矩形框的左上角坐标减去10，实现稍微高于矩形框的效果
                           # 设置字体类型和特征，字体大小为0.6，颜色为绿色，线宽为2
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0),2 )  


        # 替换文本输出目标中心坐标
                print(f"target center: x={cx}, y={cy}, area={area:.0f}, ratio={aspect_ratio:.2f}")

        else:
                print("no valid target")


#记录当前这一帧的时间
        current_time = time.time()
#1秒钟除以两帧之间的时间差，得到当前帧率
        fps = 1 / (current_time - prev_time)
#将当前帧的时间给 prev_time为下一帧计算做准备
        prev_time = current_time
 # 获取画面分辨率，frame是读到的一张图片，结构为高度 × 宽度 × 颜色通道。我们这里只
 # 取前两项shape[:2]       
        height, width = frame.shape[:2]
#把帧率和分辨率显示在画面上，即frame，位置分别是(20, 40)和(20, 80)
# 其余 信息分别是：字体大小为1，颜色为绿色，线宽为2  线宽是文字的粗细程度
# f"FPS: {fps:.1f}" 显示帧率，{fps:.1f}表示保留一位小数
#FONT_HERSHEY_SIMPLEX是OpenCV提供的一种字体
        cv2.putText(frame, f"FPS: {fps:.1f}", (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.putText(frame, f"Resolution: {width}x{height}", (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        


        # im：imagine
        # 意思是：把一张图像显示到窗口里，窗口名字来自 config.py，画面数据是 frame
        cv2.imshow(WINDOW_NAME, frame)

        # 等待键盘输入
        # 如果按下 q，就退出循环
        # cv2.waitKey(1) 表示等待 1 毫秒，
        #ord("q")把字符 "q" 转成对应的数字编码
        #& 0xFF取低八位，这是为了兼容不同平台的键盘输入
        if cv2.waitKey(1) & 0xFF == ord("q"):
                print("退出程序")
                break

    # 释放摄像头资源，关闭所有 OpenCV 窗口
    #类似于失能，disable
    cap.release()
    #关闭窗口
    cv2.destroyAllWindows()   



# 直接运行 main.py 时，会执行 main()
if __name__ == "__main__":
    main()
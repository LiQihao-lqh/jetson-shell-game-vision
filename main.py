# main.py
# 功能：
# 1. 打开 USB 摄像头
# 2. 实时读取摄像头画面
# 3. 用 OpenCV 显示画面
# 4. 按 q 退出程序
#
# 预期现象：
# 运行后弹出摄像头画面窗口，按 q 后关闭窗口并释放摄像头


#使用time模块计算帧率
import time

import cv2
from config import CAMERA_INDEX, WINDOW_NAME


def main():
    """
    主函数：
    负责打开摄像头、循环读取画面、显示画面、退出后释放资源。
    """

    # 创建摄像头对象
    # CAMERA_INDEX 来自 config.py，方便以后移植到 Jetson 时修改
    cap = cv2.VideoCapture(CAMERA_INDEX)

    # 判断摄像头是否成功打开
    if not cap.isOpened():
        print("摄像头打开失败，请检查摄像头编号或连接状态")
        return

    prev_time = time.time()

    while True:
        # 从摄像头读取一帧画面
        # ret 表示是否读取成功
        # frame 表示读取到的图像数据
        ret, frame = cap.read()

        # 如果读取失败，退出循环
        if not ret:
            print("画面读取失败")
            break

        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time
        height, width = frame.shape[:2]

        cv2.putText(frame, f"FPS: {fps:.1f}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.putText(frame, f"Resolution: {width}x{height}", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)




        # 显示当前画面
        cv2.imshow(WINDOW_NAME, frame)

        # 等待键盘输入
        # 如果按下 q，就退出循环
        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("退出程序")
            break

    # 释放摄像头资源
    cap.release()

    # 关闭所有 OpenCV 窗口
    cv2.destroyAllWindows()


# Python 程序入口
# 直接运行 main.py 时，会执行 main()
if __name__ == "__main__":
    main()
import time
import cv2

from config import (
    CAMERA_INDEX,
    WINDOW_NAME,
    FRAME_WIDTH,
    FRAME_HEIGHT,
)

from vision_detector import detect_target, draw_target
from servo_controller import ServoController
from gimbal_tracker import GimbalTracker


def main():
    # 1. 创建舵机控制对象
    servo = ServoController(port="COM4", baudrate=115200)

    # 2. 创建云台追踪对象
    tracker = GimbalTracker(servo)

    # 3. 云台回到标准状态
    servo.go_home()

    # 4. 打开摄像头，选择 V4L2 模式，（选csi摄像头的模式很卡）
    # 设置编码格式为 MJPG，分辨率和帧率
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print("摄像头打开失败")
        return

    prev_time = time.time()

    while True:
        # 5. 读取画面
        ret, frame = cap.read()
        if not ret:
            print("画面读取失败")
            break

        # 6. 视觉识别目标
        found, target = detect_target(frame)

        if found:
            # 7. 画目标框
            draw_target(frame, target)

            # 8. 调用云台锁定
            tracker.update(
                target["cx"],
                target["cy"],
                frame
            )
            #把数据打印在终端，方便调试
            print(
                f"target center: x={target['cx']}, y={target['cy']}, "
                f"area={target['area']:.0f}, ratio={target['aspect_ratio']:.2f}"
            )
        else:
            print("no valid target")

        # 9. 计算 FPS
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time

        # 10. 获取画面宽高
        height, width = frame.shape[:2]

        # 11. 画画面中心点
        cv2.circle(frame, (width // 2, height // 2), 5, (255, 0, 0), -1)

        # 12. 显示 FPS 和分辨率
        cv2.putText(frame, f"FPS: {fps:.1f}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.putText(frame, f"Resolution: {width}x{height}", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 13. 显示画面
        cv2.imshow(WINDOW_NAME, frame)

        # 14. 按 q 退出
        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("退出程序")
            break

    # 15. 释放资源
    cap.release()
    cv2.destroyAllWindows()
    servo.close()


if __name__ == "__main__":
    main()
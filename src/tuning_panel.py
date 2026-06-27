import cv2

#窗口名
WINDOW_NAME = "Tuning Panel"
# kp 使用整数滑条表示，所以这里设置放大倍数
KP_SCALE = 1000


# OpenCV 创建滑条时需要一个回调函数，但是我们这里不想在滑条变化瞬间处理，而是在主循环里每一帧主动读取滑条值
def _nothing(value):
    pass


# 创建调参窗口和四个滑条
def create_tuning_panel(tracker):
    cv2.namedWindow(WINDOW_NAME)

    # OpenCV 滑条只能用整数，kp 放大 1000 倍显示，读取时再除回来
    #200设置最大值，kp最大0.2
    cv2.createTrackbar("pan kp x1000", WINDOW_NAME, int(tracker.pan_gain * KP_SCALE), 200, _nothing)
    cv2.createTrackbar("tilt kp x1000", WINDOW_NAME, int(tracker.tilt_gain * KP_SCALE), 200, _nothing)
    cv2.createTrackbar("pan max step", WINDOW_NAME, tracker.pan_max_step, 50, _nothing)
    cv2.createTrackbar("tilt max step", WINDOW_NAME, tracker.tilt_max_step, 50, _nothing)


# 读取滑条当前值，并写回追踪器参数
def update_tracker_from_panel(tracker):
    tracker.pan_gain = cv2.getTrackbarPos("pan kp x1000", WINDOW_NAME) / KP_SCALE
    tracker.tilt_gain = cv2.getTrackbarPos("tilt kp x1000", WINDOW_NAME) / KP_SCALE
    tracker.pan_max_step = max(1, cv2.getTrackbarPos("pan max step", WINDOW_NAME))
    tracker.tilt_max_step = max(1, cv2.getTrackbarPos("tilt max step", WINDOW_NAME))

class GimbalTracker:
    def __init__(self, servo):
        self.servo = servo
#这一段的意识是：把舵机控制器从外面塞进追踪算法里，而不是让追踪算法自己去创建舵机。
#self.servo = servo 不是创建舵机，而是保存外面传进来的舵机对象


        # 舵机初始坐标，先和回中位置保持一致
        self.pan = 550
        self.tilt = 500

        # 误差转舵机坐标的比例，数值越大追踪越灵敏
        #其实就是kp
        self.pan_gain = 0.05
        self.tilt_gain = 0.05

        # 小误差不动，减少画面抖动
        self.dead_zone = 20

        # 舵机安全范围
        self.pan_min = 200
        self.pan_max = 700
        self.tilt_min = 400
        self.tilt_max = 700

    #当前思路：
    #1. 计算目标中心点与画面中心的误差。
    #2. 如果误差大于死区，根据误差调整云台舵机位置。
    #kp控制

        #读取目标的中心坐标
    def update(self, target_x, target_y, frame):

        #读取画面的宽度和高度
        height, width = frame.shape[:2]

        #计算画面中心坐标
        image_center_x = width // 2
        image_center_y = height // 2

        #计算误差
        error_x = target_x - image_center_x
        error_y = target_y - image_center_y

        #abs(error_x) 表示取误差的绝对值，确保误差为正数
        if abs(error_x) > self.dead_zone:
            #根据误差调整云台舵机位置
            self.pan -= error_x * self.pan_gain

        if abs(error_y) > self.dead_zone:
            #根据误差调整云台舵机位置
            self.tilt += error_y * self.tilt_gain

        #限制舵机位置在安全范围内.clamp：限制函数
        self.pan = self._clamp(self.pan, self.pan_min, self.pan_max)
        self.tilt = self._clamp(self.tilt, self.tilt_min, self.tilt_max)

        #移动云台舵机到新的位置
        #这里实际是在调用外部的servo = ServoController中的move_pan和move_tilt
        self.servo.move_pan(self.pan)
        self.servo.move_tilt(self.tilt)

        #返回新的云台舵机位置
        return self.pan, self.tilt
    
        #限制函数：确保舵机位置在安全范围内
        #再次限制，确保在安全范围内
    def _clamp(self, value, min_value, max_value):
        return max(min_value, min(max_value, int(value)))

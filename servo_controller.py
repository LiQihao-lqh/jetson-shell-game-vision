import time
import serial


PORT = "COM4"
BAUDRATE = 115200

# 舵机协议帧头和位置控制命令
FRAME_HEADER = 0x55
CMD_MOVE_TIME_WRITE = 1


def clamp(value, min_value, max_value):
    # 限制数值范围，防止舵机坐标超出安全范围
    return max(min_value, min(max_value, int(value)))


def send_packet(ser, servo_id, cmd, params):
    # 数据长度 = 命令 + 参数 + 校验和
    length = 3 + len(params)
    checksum = 255 - ((servo_id + length + cmd + sum(params)) % 256)

    packet = [
        FRAME_HEADER,
        FRAME_HEADER,
        servo_id,
        length,
        cmd,
    ]
    packet.extend(params)
    packet.append(checksum)

    ser.write(bytes(packet))
    ser.flush()

    print("send:", " ".join(f"{x:02X}" for x in packet))


def move_servo(ser, servo_id, position, duration=100):
    # 舵机位置范围 0~1000，运行时间单位是 ms
    position = clamp(position, 0, 1000)
    duration = clamp(duration, 20, 30000)

    # 串口一次发送 1 字节，所以位置和时间要拆成低位、高位
    pos_low = position & 0xFF
    pos_high = (position >> 8) & 0xFF
    time_low = duration & 0xFF
    time_high = (duration >> 8) & 0xFF

    params = [pos_low, pos_high, time_low, time_high]
    send_packet(ser, servo_id, CMD_MOVE_TIME_WRITE, params)


def move_pan(ser, position, duration=100):
    # 1 号舵机：左右方向
    position = clamp(position, 200, 700)
    move_servo(ser, 1, position, duration)


def move_tilt(ser, position, duration=100):
    # 2 号舵机：上下方向
    position = clamp(position, 400, 700)
    move_servo(ser, 2, position, duration)


class ServoController:
    def __init__(self, port=PORT, baudrate=BAUDRATE):
        # 打开串口，并给舵机控制板一点初始化时间
        self.ser = serial.Serial(port, baudrate, timeout=0.1)
        time.sleep(0.5)

    def move_pan(self, position, duration=100):
        # 控制左右舵机
        move_pan(self.ser, position, duration)

    def move_tilt(self, position, duration=100):
        # 控制上下舵机
        move_tilt(self.ser, position, duration)

    def go_home(self):
        # 云台回到初始中间位置
        self.move_pan(550, 500)
        self.move_tilt(500, 500)

    def close(self):
        # 关闭串口
        self.ser.close()

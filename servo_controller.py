#time模块：提供时间相关的函数，作用是延时，等待舵机响应
import time
#serial模块：提供串口通信的函数，作用是与舵机进行通信
#专用于串口通信的模块还有pyserial
#iic专用的叫smbus
#spi专用的叫spidev
import serial

#数据帧的作用
#一帧可以理解为一条完整指令
#把串口通信想象成说话。
#如果连续说：
#控制1号舵机到200位置500毫秒，控制2号舵机到500位置500毫秒
#如果没有分隔，接收方可能不知道：
#哪一句从哪里开始
#哪一句到哪里结束
#这一句是给谁的这一句有没有传错```
#所以我们把一条完整指令打包成一个“数据帧”。
#一帧就像一句完整的话：
#开头标志 + 舵机ID + 长度 + 命令 + 参数 + 校验

#整体结构：
#先把框架和流程写好，然后把具体的功能实现写在后面的函数里
#实际上不是从上往下逐步按照顺序执行的，而是按照需求跳转到对应的函数里执行
#前面只是调用了函数，但是函数具体功能写在后面了

# 改成你官方调试软件里看到的 COM 口
#PORT意思是串口，端口地址
PORT = "COM4"

#波特率：指的是串口通信的速率，单位是波特率
#不同设备通信时，波特率要一致
#1波特 = 1个字节
#此时传输控制舵机的一条命令大约0.87ms
BAUDRATE = 115200

# 幻尔总线舵机帧头
#它告诉舵机：注意，后面是一条新指令
#选0x55是因为商家sdk里面默认的是0x55
#其次0x55是01010101，0，1交替出现有特点，方便识别
FRAME_HEADER = 0x55

# 位置控制指令
#CMD = command = 命令
#MOVE = 移动
#TIME = 时间
#WRITE = 写入
#合起来：把“带时间的位置控制命令”这个命令编号定义为 1
#协议中规定
#cmd = 1   → 控制舵机转动
#cmd = 13  → 设置舵机 ID
#cmd = 14  → 读取舵机 ID
#cmd = 28  → 读取当前位置
CMD_MOVE_TIME_WRITE = 1

#clamp函数：限幅函数，防止位置超出安全范围
#clamp：限制值
#括号内分别是：要限制的值、最小值、最大值
def clamp(value, min_value, max_value):
    #这里对比了两次，目的是限制最终的输出值在最小值和最大值之间
    #分别是实际值，最小值，最大值
    return max(min_value, min(max_value, int(value)))

# send_packet函数：干活的函数，负责发送数据帧
# ser: servo：舵机
#这里cmd具体干啥要看上面的部分
def send_packet(ser, servo_id, cmd, params):
    # 数据长度 = 指令 + 参数 + 校验和
    #这里是设置数据长度，包括指令、参数、校验和三部分
    #一个长度指的是一个字节，所以指令、参数、校验和三部分的长度加起来就是数据帧的总长度
    #params 是参数列表，包含的位置和时间信息。
    #3
    length = 3 + len(params)

    # 校验和是一种简单的错误检测机制
    #校验的原因是数据传输中可能发生：
    #1. 数据帧被修改了，受噪声干扰等导致
    #2. 数据帧被截断了，线松了
    #3. 数据帧被发送了多个，波特率不匹配
    #checksum是一个变量长度为1字节
    #  %是取余
    #如果校验和等于0，说明数据帧没有被修改改过
    checksum = 255 - ((servo_id + length + cmd + sum(params)) % 256)

    # 拼接完整数据帧
    #打包数据
    #内容是：
    #帧头 帧头 舵机ID 长度 命令 参数 校验和
    #两个帧头：判断数据开头更准确
    packet = [
        FRAME_HEADER,
        FRAME_HEADER,
        servo_id,
        length,
        cmd
    ]

    #添加参数和校验和
    packet.extend(params)
    packet.append(checksum)

    # 通过串口发送
    #write：把数据写入串口缓冲区
    #bytes(packet)：把列表数据转换为字节数据
    #flush()：立即发出数据  flush 发送一片数据
    #这一步已经完成数据发送了
    ser.write(bytes(packet))
    ser.flush()

    # 打印发送的数据，方便排查
    #send字符串
    #join = 拼接
    #for = 遍历packet列表，对每个元素进行格式化输出
    #f"{x:02X}"：把每个元素x转换为两位大写十六进制字符串，用空格分隔
    print("send:", " ".join(f"{x:02X}" for x in packet))

#duration=100：不传duration是参数默认运行时间，单位 ms
def move_servo(ser, servo_id, position, duration=100):
    # 舵机通用范围 0~1000
    position = clamp(position, 0, 1000)

    # 运行时间，单位 ms
    #限幅：防止duration超出安全范围，导致舵机异常运动
    duration = clamp(duration, 20, 30000)

    #数据拆分，因为串口一格只能发 1 个字节，而 position 和 duration 可能超过 255，所以必须拆成两个字节
    #比如位置=500，500大于255，所以要拆分
    #低八位在前面

    # 位置拆成低八位和高八位
    pos_low = position & 0xFF
    pos_high = (position >> 8) & 0xFF

    # 时间拆成低八位和高八位
    time_low = duration & 0xFF
    time_high = (duration >> 8) & 0xFF

    # 参数顺序：位置低位、位置高位、时间低位、时间高位 
    params = [pos_low, pos_high, time_low, time_high]

    #这里是调用send_packet函数，规定最后要发送什么数据
    send_packet(ser, servo_id, CMD_MOVE_TIME_WRITE, params)

#move_pan函数：控制舵机1左右方向
#这里是自己封装函数
def move_pan(ser, position, duration=100):
    # pan 左右旋转，舵机专用术语
    # 你的舵机1安全范围是 200~700，标准位置是 400
    position = clamp(position, 0, 1000)
    move_servo(ser, 1, position, duration)


def move_tilt(ser, position, duration=100):
    # tilt 上下旋转，舵机专用术语
    # 你的舵机2范围是 0~1000，标准位置是 500
    position = clamp(position, 0, 1000)
    move_servo(ser, 2, position, duration)


def main():
    # 打开串口
    #with = 使用某个资源
    #timeout = 超时时间为0.1s
    #as = 以ser变量名表示串口资源
    with serial.Serial(PORT, BAUDRATE, timeout=0.1) as ser:
        print("serial opened:", PORT)

        # 给串口一点稳定时间,等待稳定
        time.sleep(0.5)

        input("确认舵机已供电，手离开舵盘后，按回车开始追踪...")

        # 回到标准状态，第二个参数500是duration
        print("go home")
        move_pan(ser, 400, 500)
        move_tilt(ser, 500, 500)
        time.sleep(1)

        # 测试舵机1
        print("test servo 1")
        move_pan(ser, 250, 500)
        time.sleep(1)

        move_pan(ser, 200, 500)
        time.sleep(1)

        # 测试舵机2
        print("test servo 2")
        move_tilt(ser, 550, 500)
        time.sleep(1)

        move_tilt(ser, 500, 500)
        time.sleep(1)

        print("test done")


if __name__ == "__main__":
    main()
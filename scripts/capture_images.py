import cv2
from pathlib import Path
import re


# =========================
# 配置区：以后主要改这里
# =========================

# =========================
# 主要改这三个 
# DATASET_ROOT = Path(r"D:\Jetson\Camera\dataset\box_obb_v1")
# SPLIT = "train"
# CAMERA_INDEX = 1
# =========================


# 数据集根目录
DATASET_ROOT = Path(r"D:\Jetson\Camera\dataset\target_card_det_v1")

# 保存到 train 还是 val
SPLIT = "train"   # 可改成 "val"

# 摄像头编号
CAMERA_INDEX = 1  # 如果打不开，改成 0

# 图片名前缀
IMAGE_PREFIX = "box_obb"

# 图片格式
IMAGE_EXT = ".jpg"

# JPG 保存质量
JPEG_QUALITY = 95

# 窗口名
WINDOW_NAME = "USB Camera"


# =========================
# 主流程
# =========================

def main():
    save_dir = DATASET_ROOT / "images" / SPLIT
    save_dir.mkdir(parents=True, exist_ok=True)

    count = get_next_index(save_dir, IMAGE_PREFIX, IMAGE_EXT)

    cap = open_camera(CAMERA_INDEX)

    if not cap.isOpened():
        print(f"摄像头打开失败，当前 CAMERA_INDEX = {CAMERA_INDEX}")
        print("可以尝试把 CAMERA_INDEX 改成 0 或 2")
        return

    print("=" * 60)
    print("拍照脚本启动成功")
    print(f"保存路径: {save_dir}")
    print(f"当前编号从: {count:04d} 开始")
    print("按 s 保存图片")
    print("按 q 或 ESC 退出")
    print("=" * 60)

    while True:
        ret, frame = cap.read()

        if not ret:
            print("读取摄像头画面失败")
            break

        show_frame = frame.copy()

        cv2.putText(
            show_frame,
            f"Save Dir: {save_dir}",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )

        cv2.putText(
            show_frame,
            f"Next: {IMAGE_PREFIX}_{count:04d}{IMAGE_EXT}",
            (20, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )

        cv2.putText(
            show_frame,
            "Press S to save, Q/ESC to quit",
            (20, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )

        cv2.imshow(WINDOW_NAME, show_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            filename = f"{IMAGE_PREFIX}_{count:04d}{IMAGE_EXT}"
            image_path = save_dir / filename

            success = cv2.imwrite(
                str(image_path),
                frame,
                [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY],
            )

            if success:
                print(f"保存成功: {image_path}")
                count += 1
            else:
                print(f"保存失败: {image_path}")

        elif key == ord("q") or key == 27:
            print("退出拍照脚本")
            break

    cap.release()
    cv2.destroyAllWindows()


# =========================
# 工具函数
# =========================

def open_camera(camera_index):
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

    if not cap.isOpened():
        cap = cv2.VideoCapture(camera_index)

    return cap


def get_next_index(save_dir, prefix, image_ext):
    pattern = re.compile(rf"^{re.escape(prefix)}_(\d+){re.escape(image_ext)}$")

    max_index = -1

    for file_path in save_dir.glob(f"*{image_ext}"):
        match = pattern.match(file_path.name)

        if match:
            index = int(match.group(1))
            max_index = max(max_index, index)

    return max_index + 1


if __name__ == "__main__":
    main()

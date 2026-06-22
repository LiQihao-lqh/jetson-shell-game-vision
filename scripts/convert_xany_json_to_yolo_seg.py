import json
from pathlib import Path


# =========================
# 配置区：以后主要改这里
# =========================


#住主要改DATASET_ROOT = Path(r"D:\Jetson\Camera\dataset\box_seg_v2")，
#不用分割改27行TARGET_SHAPE_TYPE = "polygon"


DATASET_ROOT = Path(r"D:\Jetson\Camera\dataset\box_obb_v1")

CLASSES_FILE = DATASET_ROOT / "classes.txt"

SPLITS = ["train", "val"]

# 优先从 annotations_json 读取 json
# 如果 annotations_json 里没有，再从 images 旁边读取 json
JSON_DIR_PRIORITY = [
    "annotations_json",
    "images",
]

# 只转换 polygon
TARGET_SHAPE_TYPE = "polygon"


# =========================
# 主流程
# =========================

def main():
    class_to_id = load_classes(CLASSES_FILE)

    print("=" * 60)
    print("X-AnyLabeling JSON → YOLO Segmentation TXT")
    print(f"数据集目录: {DATASET_ROOT}")
    print(f"类别文件: {CLASSES_FILE}")
    print(f"类别映射: {class_to_id}")
    print("=" * 60)

    for split in SPLITS:
        convert_split(split, class_to_id)

    print("=" * 60)
    print("转换完成")
    print("=" * 60)


def convert_split(split, class_to_id):
    json_dir = find_json_dir(split)
    label_dir = DATASET_ROOT / "labels" / split
    label_dir.mkdir(parents=True, exist_ok=True)

    if json_dir is None:
        print(f"[{split}] 没找到 json 目录，跳过")
        return

    json_files = sorted(json_dir.glob("*.json"))

    if not json_files:
        print(f"[{split}] json 目录为空: {json_dir}")
        return

    print(f"\n[{split}] 读取 json: {json_dir}")
    print(f"[{split}] 输出 labels: {label_dir}")
    print(f"[{split}] json 数量: {len(json_files)}")

    ok_count = 0
    empty_count = 0
    skip_count = 0

    for json_path in json_files:
        try:
            lines = convert_one_json(json_path, class_to_id)
        except Exception as e:
            print(f"[错误] {json_path.name}: {e}")
            skip_count += 1
            continue

        label_path = label_dir / f"{json_path.stem}.txt"

        if lines:
            label_path.write_text("\n".join(lines), encoding="utf-8")
            ok_count += 1
        else:
            # 如果没有有效 polygon，不写空文件，避免误导
            if label_path.exists():
                label_path.unlink()
            empty_count += 1
            print(f"[空标注] {json_path.name} 没有有效 polygon，未生成 txt")

    print(f"[{split}] 成功生成: {ok_count}")
    print(f"[{split}] 空标注: {empty_count}")
    print(f"[{split}] 跳过/错误: {skip_count}")


# =========================
# 转换逻辑
# =========================

def convert_one_json(json_path, class_to_id):
    data = json.loads(json_path.read_text(encoding="utf-8"))

    image_width = data.get("imageWidth")
    image_height = data.get("imageHeight")

    if not image_width or not image_height:
        raise ValueError("json 里缺少 imageWidth 或 imageHeight")

    shapes = data.get("shapes", [])
    lines = []

    for shape in shapes:
        label = shape.get("label")
        shape_type = shape.get("shape_type")
        points = shape.get("points", [])

        if shape_type != TARGET_SHAPE_TYPE:
            continue

        if label not in class_to_id:
            print(f"[警告] {json_path.name} 中 label={label} 不在 classes.txt 里，跳过")
            continue

        if len(points) < 3:
            print(f"[警告] {json_path.name} polygon 点数少于 3，跳过")
            continue

        class_id = class_to_id[label]

        normalized_points = []

        for point in points:
            x, y = point

            x_norm = x / image_width
            y_norm = y / image_height

            # 防止极少数点越界
            x_norm = clamp(x_norm, 0.0, 1.0)
            y_norm = clamp(y_norm, 0.0, 1.0)

            normalized_points.append(x_norm)
            normalized_points.append(y_norm)

        line = str(class_id) + " " + " ".join(
            f"{value:.6f}" for value in normalized_points
        )

        lines.append(line)

    return lines


# =========================
# 工具函数
# =========================

def load_classes(classes_file):
    if not classes_file.exists():
        raise FileNotFoundError(f"找不到 classes.txt: {classes_file}")

    class_names = [
        line.strip()
        for line in classes_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if not class_names:
        raise ValueError("classes.txt 为空")

    return {name: index for index, name in enumerate(class_names)}


def find_json_dir(split):
    for folder_name in JSON_DIR_PRIORITY:
        candidate = DATASET_ROOT / folder_name / split

        if candidate.exists():
            json_files = list(candidate.glob("*.json"))

            if json_files:
                return candidate

    return None


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


if __name__ == "__main__":
    main()
    
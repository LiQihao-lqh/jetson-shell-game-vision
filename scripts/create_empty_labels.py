from pathlib import Path


IMAGE_DIR = Path(r"D:\Jetson\Camera\dataset\target_card_det_v1\images\val")
LABEL_DIR = Path(r"D:\Jetson\Camera\dataset\target_card_det_v1\labels\val")

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


created_count = 0
existing_count = 0
image_count = 0


LABEL_DIR.mkdir(parents=True, exist_ok=True)


for image_path in sorted(IMAGE_DIR.iterdir()):
    if not image_path.is_file():
        continue

    if image_path.suffix.lower() not in IMAGE_EXTS:
        continue

    image_count += 1

    label_path = LABEL_DIR / f"{image_path.stem}.txt"

    if label_path.exists():
        existing_count += 1
        continue

    label_path.write_text("", encoding="utf-8")
    print("创建空标签:", label_path)
    created_count += 1


print("处理完成")
print("扫描图片数量:", image_count)
print("新建空标签数量:", created_count)
print("已有标签数量:", existing_count)
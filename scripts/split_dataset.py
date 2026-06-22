from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]

img_val = root / "dataset" / "images" / "val"

label_train = root / "dataset" / "labels" / "train"
label_val = root / "dataset" / "labels" / "val"

label_val.mkdir(parents=True, exist_ok=True)

image_exts = [".jpg", ".jpeg", ".png"]

moved_count = 0
missing_count = 0

for img_path in img_val.iterdir():
    if img_path.suffix.lower() not in image_exts:
        continue

    label_name = img_path.stem + ".txt"

    src_label = label_train / label_name
    dst_label = label_val / label_name

    if src_label.exists():
        shutil.move(str(src_label), str(dst_label))
        print("移动标签:", src_label, "->", dst_label)
        moved_count += 1
    else:
        print("缺少标签:", src_label)
        missing_count += 1

print("标签移动完成")
print("成功移动:", moved_count)
print("缺少标签:", missing_count)
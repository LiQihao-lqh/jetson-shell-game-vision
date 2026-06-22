from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]

img_val = root / "dataset" / "images" / "val"

label_train = root / "dataset" / "labels" / "train"
label_val = root / "dataset" / "labels" / "val"

label_val.mkdir(parents=True, exist_ok=True)

image_exts = {".jpg", ".jpeg", ".png"}

moved_count = 0
kept_empty_count = 0
conflict_count = 0
missing_count = 0

for img_path in img_val.iterdir():
    if img_path.suffix.lower() not in image_exts:
        continue

    label_name = img_path.stem + ".txt"

    src_label = label_train / label_name
    dst_label = label_val / label_name

    if src_label.exists():
        if dst_label.exists():
            if dst_label.stat().st_size == 0:
                dst_label.unlink()
                print("删除错误空标签:", dst_label)
            else:
                print("警告：val 已有非空标签，train 也有同名标签:", label_name)
                conflict_count += 1
                continue

        shutil.move(str(src_label), str(dst_label))
        print("移动真实标签:", src_label, "->", dst_label)
        moved_count += 1

    else:
        if dst_label.exists():
            if dst_label.stat().st_size == 0:
                print("保留空标签:", dst_label)
                kept_empty_count += 1
            else:
                print("保留已有非空标签:", dst_label)
        else:
            dst_label.write_text("", encoding="utf-8")
            print("创建空标签，请确认这是负样本:", dst_label)
            missing_count += 1

print("修复完成")
print("移动真实标签:", moved_count)
print("保留空标签:", kept_empty_count)
print("冲突数量:", conflict_count)
print("新建空标签:", missing_count)

from ultralytics import YOLO

model = YOLO(r"D:\Jetson\Camera\runs\detect\red_box_v2\weights\best.pt")

model.train(
    data="data.yaml",
    epochs=60,
    imgsz=640,
    batch=8,
    device=0,
    workers=0,
    name="red_box_v3"
)
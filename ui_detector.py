from ultralytics import YOLO
import cv2

# load pretrained model
model = YOLO("yolov8n.pt")


def detect_ui_elements(image_path):

    results = model(image_path)

    elements = []

    img = cv2.imread(image_path)

    for r in results:

        boxes = r.boxes

        for box in boxes:

            x1, y1, x2, y2 = box.xyxy[0]

            x = int((x1 + x2) / 2)
            y = int((y1 + y2) / 2)

            cls = int(box.cls[0])

            label = model.names[cls]

            elements.append({
                "type": label,
                "x": x,
                "y": y
            })

    return elements
from ultralytics import YOLO

class ObjectDetector:

    def __init__(self):
        self.model = YOLO("yolo11n.pt")

    def detect(self, frame):

        results = self.model(
            frame,
            verbose=False
        )

        people = 0
        vehicles = 0

        for box in results[0].boxes:

            class_id = int(box.cls[0])

            # COCO class 0 = Person
            if class_id == 0:
                people += 1

            # Vehicle classes
            if class_id in [2, 3, 5, 7]:
                vehicles += 1

        output = results[0].plot()

        return output, people, vehicles

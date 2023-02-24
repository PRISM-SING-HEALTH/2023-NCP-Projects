from ultralytics import YOLO

model = YOLO("yolov8n.pt")  # load a pretrained YOLOv8n model

model.train(data="data.yaml")  # train the model
model.val()  # evaluate model performance on the validation set
model.export(format="onnx")  # export the model to ONNX format
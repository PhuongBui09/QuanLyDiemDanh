import cv2
import numpy as np
from keras.models import load_model
import yaml

class Camera:
    def __init__(self, model_path, labels_file):
        self.cap = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.model = load_model(model_path)
        self.predicted_student_id = None
        self.has_predicted = False
        
        with open(labels_file, 'r') as file:
            self.labels = yaml.safe_load(file)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (320, 240))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                roi_color = frame[y:y+h, x:x+w]
                roi_color = cv2.resize(roi_color, (224, 224))
                roi_color = roi_color.astype('float32') / 255.0
                roi_color = np.expand_dims(roi_color, axis=0)

                # Dự đoán chỉ khi đã nhấn nút xác nhận
                if self.has_predicted:
                    prediction = self.model.predict(roi_color)
                    predicted_label = np.argmax(prediction)
                    print(predicted_label)
                    # Lấy mã sinh viên từ nhãn
                    if predicted_label < len(self.labels):
                        label = self.labels[predicted_label]
                        self.predicted_student_id = label.split('_')[-1]  # Tách số cuối cùng từ nhãn
                    self.has_predicted = False  # Đặt lại sau khi dự đoán

            return frame

    def reset_prediction(self):
        self.has_predicted = False

    def release(self):
        self.cap.release()
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.applications import VGG16
from tensorflow.keras import Model
from tensorflow.keras.callbacks import EarlyStopping

# Đường dẫn đến thư mục dữ liệu
data_dir = "StudentData"

# Chuẩn bị tập dữ liệu với ImageDataGenerator
datagen = ImageDataGenerator(rescale=1.0/255, validation_split=0.2)  # Chia 20% cho tập validation

# Tạo generator cho tập huấn luyện
train_generator = datagen.flow_from_directory(
    data_dir,
    target_size=(224, 224),  # Kích thước ảnh sau khi resize (VGG16 yêu cầu 224x224)
    batch_size=32,  # Số lượng ảnh trong mỗi batch
    class_mode='categorical',  # Đa phân loại
    subset='training'  # Tập huấn luyện
)

# Tạo generator cho tập validation
validation_generator = datagen.flow_from_directory(
    data_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    subset='validation'  # Tập validation
)

# In ra các nhãn
print("Classes:", train_generator.class_indices)

# Tải mô hình VGG16
base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# Đóng băng các lớp của VGG16
for layer in base_model.layers:
    layer.trainable = False

# Xây dựng mô hình
x = base_model.output
x = Flatten()(x)
x = Dense(128, activation='relu')(x)
predictions = Dense(train_generator.num_classes, activation='softmax')(x)  # Số lớp = số sinh viên

# Tạo mô hình hoàn chỉnh
model = Model(inputs=base_model.input, outputs=predictions)

# Compile mô hình
model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])

# Định nghĩa callback EarlyStopping
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# Huấn luyện mô hình với callback EarlyStopping
history = model.fit(
    train_generator,
    epochs=10,  # Số lần lặp qua toàn bộ tập dữ liệu
    validation_data=validation_generator,
    callbacks=[early_stopping]  # Thêm EarlyStopping vào callbacks
)

# Lưu mô hình
model.save('student_face_classifier.keras')
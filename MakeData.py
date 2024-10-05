import os
import cv2
import sqlite3
from tkinter import Tk, Label, Entry, Button, messagebox
from werkzeug.utils import secure_filename
import time

# Kết nối đến cơ sở dữ liệu SQLite
conn = sqlite3.connect('sqlite.db')  
cursor = conn.cursor()

def capture_images(student_id, student_name):
    # Sử dụng secure_filename để chuyển tên sinh viên thành tên an toàn
    safe_student_name = secure_filename(student_name)
    
    # Tạo thư mục lưu ảnh nếu chưa tồn tại
    folder_name = f"StudentData/{safe_student_name}_{student_id}"
    print("Thư mục lưu ảnh:", folder_name)  # In ra thư mục lưu ảnh để kiểm tra

    # Kiểm tra nếu thư mục đã tồn tại và chứa ít nhất 1 ảnh
    if os.path.exists(folder_name) and len(os.listdir(folder_name)) > 0:
        # Hỏi người dùng có muốn cập nhật ảnh không
        response = messagebox.askyesno("Thông báo", "Đã tồn tại ảnh cho sinh viên này. Bạn có muốn cập nhật lại không?")
        if not response:
            return  # Nếu người dùng chọn "Không", dừng quá trình chụp ảnh
    
    # Tạo thư mục nếu chưa tồn tại
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Khởi tạo camera
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    count = 0
    last_capture_time = 0  # Biến lưu thời gian chụp ảnh cuối cùng

    while count < 50:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Chuyển đổi ảnh sang màu xám để phát hiện khuôn mặt
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        # Vẽ hình chữ nhật xung quanh khuôn mặt trên ảnh màu
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Cắt ảnh khuôn mặt từ ảnh màu
            face_region_color = frame[y:y + h, x:x + w]  # Sử dụng ảnh màu

            # Lưu ảnh khuôn mặt nếu đã qua 0.3 giây kể từ lần chụp trước
            current_time = time.time()
            if current_time - last_capture_time >= 0.3:
                count += 1
                img_path = os.path.join(folder_name, f'image_{count}.jpg')
                cv2.imwrite(img_path, face_region_color)  # Lưu vùng khuôn mặt màu
                last_capture_time = current_time  # Cập nhật thời gian chụp
                 
                print('Đã lưu ảnh khuôn mặt tại:', img_path)

        # Hiển thị khung hình với các hình chữ nhật quanh khuôn mặt
        cv2.imshow('Face Detection', frame)

        # Nhấn 'q' để thoát
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def check_student():
    student_id = student_id_entry.get()
    cursor.execute("SELECT * FROM Student WHERE StudentID=?", (student_id,))
    student = cursor.fetchone()

    if student:
        student_name = student[1]
        capture_images(student_id, student_name)
    else:
        messagebox.showerror("Lỗi", "Mã sinh viên không tồn tại trong cơ sở dữ liệu!")

# Tạo cửa sổ chính
root = Tk()
root.title("Chụp ảnh sinh viên")
root.geometry("300x200")

# Nhãn và ô nhập mã sinh viên
label = Label(root, text="Nhập mã sinh viên:")
label.pack(pady=10)
student_id_entry = Entry(root)
student_id_entry.pack(pady=10)

# Nút kiểm tra và chụp ảnh
check_button = Button(root, text="Kiểm tra và chụp ảnh", command=check_student)
check_button.pack(pady=20)

root.mainloop()

# Đóng kết nối cơ sở dữ liệu
conn.close()

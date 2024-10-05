import tkinter as tk
from database import Database
from gui import GUI
from camera import Camera

db = Database()
camera = Camera('student_face_classifier.keras', 'labels.yaml')

root = tk.Tk()
gui = GUI(root, db, camera)

# Bắt đầu cập nhật khung camera
gui.update_frame()
root.mainloop()

# Giải phóng tài nguyên
camera.release()
db.close()

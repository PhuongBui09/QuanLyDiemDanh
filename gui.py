import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import threading
import queue
import datetime

class GUI:
    def __init__(self, root, database, camera):
        self.database = database
        self.camera = camera
        self.selected_course_id = None

        self.root = root
        self.root.title("Điểm danh sinh viên")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="#f0f0f0")

        # Khởi tạo các biến StringVar cho dropdowns
        self.department_var = tk.StringVar()
        self.teacher_var = tk.StringVar()
        self.semester_var = tk.StringVar()
        self.course_var = tk.StringVar()

        # Khung chính để chứa tất cả các thành phần và hiển thị ở giữa màn hình
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(expand=True, pady=0)  # Đặt pady=0

        # Khung trái chứa camera và thông tin sinh viên
        self.left_frame = tk.Frame(self.main_frame, bg="#f0f0f0", relief="ridge", bd=2)
        self.left_frame.grid(row=0, column=0, padx=20, pady=0)  # Đặt pady=0

        # Khung phải chứa dropdown và danh sách sinh viên
        self.right_frame = tk.Frame(self.main_frame, bg="#f0f0f0", bd=2)
        self.right_frame.grid(row=0, column=1, padx=20, pady=0)  # Đặt pady=0

        # Label hiển thị camera
        self.camera_label = tk.Label(self.left_frame, bg="#f0f0f0", borderwidth=2, relief="solid")
        self.camera_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Tạo frame cho các dropdown và nhãn
        self.dropdown_frame = tk.Frame(self.right_frame, bg="#f0f0f0")
        self.dropdown_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # Tạo dropdowns và nhãn
        self.create_dropdowns()

        # Nhãn hiển thị thông tin sinh viên
        self.student_info_label = tk.Label(self.left_frame, text="", font=('Helvetica', 16, 'bold'), bg="#f0f0f0")
        self.student_info_label.grid(row=1, column=0, padx=10, pady=10)

        # Khung chứa danh sách sinh viên và danh sách sinh viên có mặt
        self.listbox_frame = tk.Frame(self.left_frame, bg="#f0f0f0")
        self.listbox_frame.grid(row=2, column=0, padx=10, pady=10)

        # **Di chuyển nhãn thông báo vào khung listbox_frame**
        self.thongbao_label = tk.Label(self.listbox_frame, text="", font=('Helvetica', 16, 'bold'), bg="#f0f0f0", fg="red")
        self.thongbao_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        # Nhãn hiển thị "Danh sách sinh viên"
        self.student_list_label = tk.Label(self.listbox_frame, text="Danh sách sinh viên:", font=('Helvetica', 16, 'bold'), bg="#f0f0f0")
        self.student_list_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Listbox để hiển thị danh sách sinh viên
        self.student_listbox = tk.Listbox(self.listbox_frame, width=40, height=10, font=('Helvetica', 14), borderwidth=2, relief="solid")
        self.student_listbox.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        # Scrollbar cho Listbox
        self.student_scrollbar = tk.Scrollbar(self.listbox_frame)
        self.student_scrollbar.grid(row=2, column=1, sticky="ns")
        self.student_listbox.config(yscrollcommand=self.student_scrollbar.set)
        self.student_scrollbar.config(command=self.student_listbox.yview)

        # Nhãn hiển thị "Sinh viên có mặt"
        self.present_list_label = tk.Label(self.listbox_frame, text="Sinh viên có mặt:", font=('Helvetica', 16, 'bold'), bg="#f0f0f0")
        self.present_list_label.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        # Listbox hiển thị danh sách sinh viên có mặt
        self.present_listbox = tk.Listbox(self.listbox_frame, width=40, height=10, font=('Helvetica', 14), borderwidth=2, relief="solid")
        self.present_listbox.grid(row=2, column=2, padx=10, pady=5, sticky="nsew")

        # Scrollbar cho danh sách sinh viên có mặt
        self.present_scrollbar = tk.Scrollbar(self.listbox_frame)
        self.present_scrollbar.grid(row=2, column=3, sticky="ns")
        self.present_listbox.config(yscrollcommand=self.present_scrollbar.set)
        self.present_scrollbar.config(command=self.present_listbox.yview)

        # Queue để truyền khung hình từ luồng camera
        self.frame_queue = queue.Queue()

        # Bắt đầu luồng camera
        self.camera_thread = threading.Thread(target=self.update_camera_frame)
        self.camera_thread.daemon = True
        self.camera_thread.start()

        # Cập nhật giao diện từ queue
        self.update_frame()

    def create_dropdowns(self):
        # Tạo khung chính chứa camera và các dropdown
        self.camera_frame = tk.Frame(self.left_frame, bg="#e6e6e6")
        self.camera_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")  # Đặt khung này ở `left_frame`
        self.camera_frame.grid_columnconfigure(0, weight=3)  # Cột trái cho camera
        self.camera_frame.grid_columnconfigure(1, weight=1)  # Cột phải cho dropdown

        # Khung con trái hiển thị camera
        self.left_subframe = tk.Frame(self.camera_frame, bg="#e6e6e6", relief="ridge", bd=2)  # Khung bên trái chứa camera
        self.left_subframe.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Khung con phải chứa dropdown và các nút
        self.right_subframe = tk.Frame(self.camera_frame, bg="#e6e6e6", relief="ridge", bd=2)  # Khung bên phải chứa dropdown và nút
        self.right_subframe.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.right_subframe.grid_columnconfigure(0, weight=1)

        # Điều chỉnh hiển thị camera trong `left_subframe`
        self.camera_label = tk.Label(self.left_subframe, bg="#e6e6e6")
        self.camera_label.pack(padx=10, pady=10, expand=True, fill="both")  # Dùng `pack` để giãn đều khung camera

        # Khung dropdowns trong `right_subframe`
        self.dropdown_frame = tk.Frame(self.right_subframe, bg="#e6e6e6")  # Khung chứa dropdown
        self.dropdown_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Tạo các dropdown như bình thường
        tk.Label(self.dropdown_frame, text="Khoa:", bg="#e6e6e6", font=('Helvetica', 12)).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.department_dropdown = ttk.Combobox(self.dropdown_frame, textvariable=self.department_var, state='readonly', font=('Helvetica', 12))
        self.department_dropdown['values'] = self.database.get_departments()
        self.department_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.department_dropdown.bind("<<ComboboxSelected>>", self.on_department_change)

        tk.Label(self.dropdown_frame, text="Giảng Viên:", bg="#e6e6e6", font=('Helvetica', 12)).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.teacher_dropdown = ttk.Combobox(self.dropdown_frame, textvariable=self.teacher_var, state='readonly', font=('Helvetica', 12))
        self.teacher_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        self.teacher_dropdown.bind("<<ComboboxSelected>>", self.on_teacher_change)

        tk.Label(self.dropdown_frame, text="Học Kỳ:", bg="#e6e6e6", font=('Helvetica', 12)).grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.semester_dropdown = ttk.Combobox(self.dropdown_frame, textvariable=self.semester_var, state='readonly', font=('Helvetica', 12))
        self.semester_dropdown.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        self.semester_dropdown.bind("<<ComboboxSelected>>", self.on_semester_change)

        tk.Label(self.dropdown_frame, text="Môn Học:", bg="#e6e6e6", font=('Helvetica', 12)).grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.course_dropdown = ttk.Combobox(self.dropdown_frame, textvariable=self.course_var, state='readonly', font=('Helvetica', 12))
        self.course_dropdown.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        self.course_dropdown.bind("<<ComboboxSelected>>", self.on_course_change)

        # Nút xác nhận và thoát nằm dưới dropdowns
        submit_button = tk.Button(self.right_subframe, text="Xác nhận", command=self.on_submit, bg="#4CAF50", fg="white", font=('Helvetica', 14, 'bold'))
        submit_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        exit_button = tk.Button(self.right_subframe, text="Thoát", command=self.on_exit, bg="#f44336", fg="white", font=('Helvetica', 14, 'bold'))
        exit_button.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    def create_submit_button(self):
        submit_button = tk.Button(self.right_frame, text="Xác nhận", command=self.on_submit, bg="#4CAF50", fg="white", font=('Helvetica', 14, 'bold'))
        submit_button.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        exit_button = tk.Button(self.right_frame, text="Thoát", command=self.on_exit, bg="#f44336", fg="white", font=('Helvetica', 14, 'bold'))
        exit_button.grid(row=5, column=0, padx=10, pady=10, sticky="ew")

    def on_exit(self):
        self.root.quit()

    def update_camera_frame(self):
        while True:
            frame = self.camera.update_frame()
            if frame is not None:
                self.frame_queue.put(frame)

    def update_frame(self):
        try:
            frame = self.frame_queue.get_nowait()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)
        except queue.Empty:
            pass

        self.camera_label.after(10, self.update_frame)

    def on_department_change(self, event):
        selected_department = self.department_var.get()
        teachers = self.database.get_teachers(selected_department)
        self.teacher_dropdown['values'] = teachers
        self.teacher_dropdown.set('')

    def on_teacher_change(self, event):
        selected_teacher = self.teacher_var.get()
        semesters = self.database.get_semesters(selected_teacher)
        self.semester_dropdown['values'] = semesters
        self.semester_dropdown.set('')

    def on_semester_change(self, event):
        selected_teacher = self.teacher_var.get()
        selected_semester = self.semester_var.get()
        courses = self.database.get_courses(selected_teacher, selected_semester)
        
        # Lưu mapping từ tên môn học sang course_id
        self.course_mapping = {name: course_id for course_id, name in courses}
        
        # Hiển thị tên môn học trong dropdown
        self.course_dropdown['values'] = list(self.course_mapping.keys())
        self.course_dropdown.set('')

    def on_course_change(self, event):
        selected_course_name = self.course_var.get()
        if selected_course_name in self.course_mapping:
            self.selected_course_id = self.course_mapping[selected_course_name]
            # Lấy danh sách tất cả sinh viên đăng ký cho môn học này
            students = self.database.get_students_by_course(selected_course_name)
            self.update_student_listbox(students)  # Cập nhật danh sách sinh viên đăng ký
            
            # Load danh sách sinh viên có mặt
            self.load_present_students(self.selected_course_id)

    def update_student_listbox(self, students):
        self.student_listbox.delete(0, tk.END)  # Xóa danh sách hiện tại

        for student in students:
            student_id = student[0]
            student_name = student[1]
            # Hiển thị tên và mã sinh viên
            self.student_listbox.insert(tk.END, f"{student_name} - {student_id}")

    # Hàm load danh sách sinh viên có mặt
    def load_present_students(self, course_id):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        present_students = self.database.student_Present(course_id, current_date)
        # Cập nhật danh sách sinh viên có mặt
        self.update_present_listbox(present_students)

    def update_present_listbox(self, present_students):
        self.present_listbox.delete(0, tk.END)  # Xóa danh sách hiện tại

        for student in present_students:
            student_id = student[0]
            student_name = student[1]
            attendance_date = student[4]  # Ngày điểm danh từ kết quả truy vấn
            # Hiển thị tên, mã sinh viên và ngày điểm danh
            self.present_listbox.insert(tk.END, f"{student_name} - {student_id} - {attendance_date}")

    def on_submit(self):
        self.camera.reset_prediction()  # Reset biến trước khi xác nhận
        self.camera.has_predicted = True  # Đặt cờ để camera dự đoán

        # Đợi camera dự đoán (với thời gian timeout tối đa là 3 giây)
        timeout = 30  # 30 lần x 100ms = 3 giây
        while timeout > 0 and self.camera.predicted_student_id is None:
            self.root.update()  # Cập nhật giao diện để nhận diện khuôn mặt
            self.root.after(100)  # Đợi 100ms
            timeout -= 1

        # Kiểm tra xem mã sinh viên đã được dự đoán hay chưa
        if not self.camera.predicted_student_id:
            self.thongbao_label.config(text="Không nhận diện được khuôn mặt. Vui lòng thử lại.")
            return

        selected_course = self.course_var.get()

        # Kiểm tra xem có môn học nào đã được chọn chưa
        if not selected_course:
            self.thongbao_label.config(text="Vui lòng chọn môn học trước khi điểm danh.")
            return

        student_id = str(self.camera.predicted_student_id)  # Chuyển đổi thành chuỗi

        # Lấy danh sách sinh viên đã đăng ký cho môn học này
        students_in_course = self.database.get_students_by_course(selected_course)

        # Kiểm tra xem sinh viên đã dự đoán có nằm trong danh sách sinh viên không
        if not any(str(student[0]) == student_id for student in students_in_course):
            self.thongbao_label.config(text="Bạn không ở trong lớp này.")
            return

        # Kiểm tra nếu sinh viên đã điểm danh trong ngày **SAU KHI camera trả về predicted_student_id**
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        student_course_id = self.database.get_student_course_id(student_id, self.selected_course_id)
        if self.database.has_attended_today(student_course_id[0], current_date):
            self.thongbao_label.config(text="Sinh viên đã được điểm danh trong ngày.")
            return

        # Nếu sinh viên chưa điểm danh, lưu lại điểm danh
        student_info = self.database.get_student_info(student_id)

        if student_info:
            student_name, student_class = student_info
            self.student_info_label.config(text=f"{student_name}, lớp: {student_class}")
            self.database.save_attendance(student_course_id[0], current_date, 'Present')
            self.update_student_listbox(students_in_course)
            self.load_present_students(self.selected_course_id)
            self.camera.predicted_student_id = None  # Đặt lại sau khi điểm danh xong
        else:
            self.thongbao_label.config(text="Không tìm thấy thông tin sinh viên.")

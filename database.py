import sqlite3

class Database:
    def __init__(self, db_name='sqlite.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def get_departments(self):
        self.cursor.execute("SELECT Name FROM Department")
        return [row[0] for row in self.cursor.fetchall()]

    def get_teachers(self, department_name):
        self.cursor.execute("""
            SELECT Teacher.Name FROM Teacher 
            JOIN Department ON Teacher.DepartmentID = Department.DepartmentID 
            WHERE Department.Name = ?
        """, (department_name,))
        return [row[0] for row in self.cursor.fetchall()]

    def get_semesters(self, teacher_name):
        self.cursor.execute("""
            SELECT DISTINCT Semester.Name FROM Semester 
            JOIN SemesterCourse ON Semester.SemesterID = SemesterCourse.SemesterID 
            JOIN TeacherCourse ON SemesterCourse.CourseID = TeacherCourse.CourseID 
            JOIN Teacher ON Teacher.TeacherID = TeacherCourse.TeacherID 
            WHERE Teacher.Name = ?
        """, (teacher_name,))
        return [row[0] for row in self.cursor.fetchall()]

    def get_courses(self, teacher_name, semester_name):
        self.cursor.execute("""
            SELECT DISTINCT Course.CourseID, Course.Name FROM Course 
            JOIN SemesterCourse ON Course.CourseID = SemesterCourse.CourseID 
            JOIN Semester ON SemesterCourse.SemesterID = Semester.SemesterID 
            JOIN TeacherCourse ON Course.CourseID = TeacherCourse.CourseID 
            JOIN Teacher ON Teacher.TeacherID = TeacherCourse.TeacherID 
            WHERE Teacher.Name = ? AND Semester.Name = ?
        """, (teacher_name, semester_name))
        return [(row[0], row[1]) for row in self.cursor.fetchall()]

    def save_attendance(self, student_course_id, date, status):
        self.cursor.execute("""
            INSERT INTO Attendance (StudentCourseID, Date, Status) 
            VALUES (?, ?, ?)
        """, (student_course_id, date, status))
        self.conn.commit()

    def get_student_info(self, student_id):
        self.cursor.execute("""
            SELECT S.StudentID, S.Name, C.Name FROM Student S
            JOIN Class C ON S.ClassID = C.ClassID
            WHERE StudentID = ?
        """, (student_id,))
        return self.cursor.fetchone()
    
    def get_students_by_course(self, course_name):
        self.cursor.execute("""
            SELECT S.StudentID, S.Name FROM Student S
            JOIN StudentCourse SC ON S.StudentID = SC.StudentID
            JOIN Course C ON SC.CourseID = C.CourseID
            WHERE C.Name = ?
        """, (course_name,))
        return self.cursor.fetchall()  
    
    def has_attended_today(self, student_course_id, date):
        self.cursor.execute("""
            SELECT COUNT(*) FROM Attendance 
            WHERE StudentCourseID = ? AND Date = ?
        """, (student_course_id, date))
        return self.cursor.fetchone()[0] > 0
    
    def student_Present(self, course_id, date):
        query = """
            SELECT 
                Student.StudentID, 
                Student.Name, 
                Student.Email, 
                Student.Phone,
                Attendance.Date, 
                Attendance.Status
            FROM 
                Attendance
            JOIN 
                StudentCourse ON Attendance.StudentCourseID = StudentCourse.StudentCourseID
            JOIN 
                Student ON StudentCourse.StudentID = Student.StudentID
            JOIN 
                Course ON StudentCourse.CourseID = Course.CourseID
            WHERE 
                Course.CourseID = ? 
                AND Attendance.Date = ?
                AND Attendance.Status = 'Present'
            """
        self.cursor.execute(query, (course_id, date))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

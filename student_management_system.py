import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import arabic_reshaper
from bidi.algorithm import get_display
import webbrowser
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import tkinter as tk
from tkinter import messagebox
import json
import os
import tempfile
from datetime import datetime
import jdatetime
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(
    TTFont(
        "Vazir",
        "Fonts/Vazirmatn-Regular.ttf"
    )
)

def fa(text):
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)

# 👇 داده‌ها
users = {}
teachers = {}
students = {}
courses = {}
assignments = {}
grades = {}
student_selections = {}

def load_all_data():
    global users, teachers, students, courses, assignments, grades, student_selections
    try:
        if os.path.exists("school_data.json"):
            with open("school_data.json", "r", encoding="utf-8") as f:
                data = json.load(f)

                users.update(data.get("users", {}))
                teachers.update(data.get("teachers", {}))

                # حذف رکورد خراب استاد بدون نام کاربری
                if "" in teachers:
                    del teachers[""]

                students.update(data.get("students", {}))
                courses.update(data.get("courses", {}))
                assignments.update(data.get("assignments", {}))
                grades.update(data.get("grades", {}))
                student_selections.update(data.get("student_selections", {}))
    except: pass

def save_all_data():
    data = {
        "users": users, "teachers": teachers, "students": students,
        "courses": courses, "assignments": assignments,
        "grades": grades, "student_selections": student_selections
    }
    try:
        with open("school_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except: pass

load_all_data()

# اگر ادمین وجود نداشت، ایجادش کن
if "admin" not in users:
    users["admin"] = {
        "password": "admin",
        "role": "admin"
    }

# ---------------- App ----------------
root = tk.Tk()
root.title("سیستم دانشگاه")
root.geometry("800x600")  # به جای 700x500
# =================== Theme ===================

BG = "#F4F7FC"
CARD = "#FFFFFF"

PRIMARY = "#2563EB"
SUCCESS = "#16A34A"
DANGER = "#DC2626"
WARNING = "#F59E0B"

TEXT = "#1F2937"

TITLE_FONT = ("Tahoma", 20, "bold")
HEADER_FONT = ("Tahoma", 15, "bold")
NORMAL_FONT = ("Tahoma", 11)

root.configure(bg=BG)

def modern_button(parent, text, command, color=PRIMARY):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg="white",
        activebackground=color,
        activeforeground="white",
        relief="flat",
        bd=0,
        padx=12,
        pady=6,
        font=("Tahoma", 10, "bold"),
        cursor="hand2"
    )
# -------- Frames --------
# -------- Frames --------
login_frame = tk.Frame(root, bg=BG)
admin_frame = tk.Frame(root, bg=BG)
teacher_frame = tk.Frame(root, bg=BG)
student_frame = tk.Frame(root, bg=BG)
teacher_grade_frame = tk.Frame(root, bg=BG)
teacher_report_frame = tk.Frame(root, bg=BG)
student_select_frame = tk.Frame(root, bg=BG)
student_report_frame = tk.Frame(root, bg=BG)

for f in (login_frame, admin_frame, teacher_frame, student_frame, teacher_grade_frame, teacher_report_frame, student_select_frame, student_report_frame):
    f.place(x=0, y=0, width=800, height=600)


# ---------------- Helper ----------------
# ---------------- Helper ----------------
def show_frame(frame):
    frame.tkraise()
def clear_window():
    for frame in (
        login_frame,
        admin_frame,
        teacher_frame,
        student_frame,
        teacher_grade_frame,
        teacher_report_frame,
        student_select_frame,
        student_report_frame
    ):
        for widget in frame.winfo_children():
            widget.destroy()

def clear_window():
    for frame in (
        login_frame,
        admin_frame,
        teacher_frame,
        student_frame,
        teacher_grade_frame,
        teacher_report_frame,
        student_select_frame,
        student_report_frame
    ):
        for widget in frame.winfo_children():
            widget.destroy()


# ---------------- Login ----------------
title = tk.Label(
    login_frame,
    text="🎓 سیستم مدیریت دانشگاه",
    bg=BG,
    fg=PRIMARY,
    font=("Tahoma", 22, "bold")
)
title.pack(pady=(40,10))

subtitle = tk.Label(
    login_frame,
    text="لطفاً نام کاربری و رمز عبور خود را وارد کنید",
    bg=BG,
    fg=TEXT,
    font=("Tahoma", 11)
)
subtitle.pack(pady=(0,25))

form_frame = tk.Frame(
    login_frame,
    bg="white",
    bd=1,
    relief="solid"
)

form_frame.pack(
    pady=15,
    ipadx=25,
    ipady=20
)

tk.Label(
    form_frame,
    text="نام کاربری",
    bg="white",
    font=("Tahoma",11,"bold")
).grid(row=0,column=0,padx=10,pady=10,sticky="e")

tk.Label(
    form_frame,
    text="رمز عبور",
    bg="white",
    font=("Tahoma",11,"bold")
).grid(row=1,column=0,padx=10,pady=10,sticky="e")

username_entry = tk.Entry(
    form_frame,
    font=("Tahoma",11),
    width=25
)

password_entry = tk.Entry(
    form_frame,
    show="*",
    font=("Tahoma",11),
    width=25
)
username_entry.grid(row=0, column=1)
password_entry.grid(row=1, column=1)


def login():
    global current_teacher, current_student
    u_raw = username_entry.get()
    u = u_raw.strip().lower()
    p = password_entry.get()

    if u == "admin" and p == "admin":
        setup_admin_frame()
        show_frame(admin_frame)
        return

    # چک اساتید
    for t_key in teachers:
        if t_key.strip().lower() == u and teachers[t_key]["password"] == p:
            current_teacher = t_key
            setup_teacher_frame()
            show_frame(teacher_frame)
            return

    # چک دانشجویان
    for s_key in students:
        if s_key.strip().lower() == u and students[s_key]["password"] == p:
            current_student = s_key
            setup_student_frame()
            show_frame(student_frame)
            return

    messagebox.showerror("خطا", "نام کاربری یا رمز اشتباه!")
tk.Button(
    login_frame,
    text="🔐 ورود به سیستم",
    command=login,
    bg=PRIMARY,
    fg="white",
    activebackground=PRIMARY,
    activeforeground="white",
    relief="flat",
    cursor="hand2",
    font=("Tahoma",11,"bold"),
    width=22,
    height=2
).pack(pady=25)


# ---------------- Admin ----------------
def setup_admin_frame():
    for widget in admin_frame.winfo_children():
        widget.destroy()

    # ===== Header =====
    header = tk.Frame(admin_frame, bg=PRIMARY, height=90)
    header.pack(fill='x')

    tk.Label(
        header,
        text='🎓 پنل مدیریت دانشگاه',
        bg=PRIMARY,
        fg='white',
        font=TITLE_FONT
    ).pack(pady=22)

    # ===== Main Card =====
    card = tk.Frame(
        admin_frame,
        bg=CARD,
        bd=0,
        highlightbackground='#E5E7EB',
        highlightthickness=1
    )
    card.pack(pady=35, padx=40, fill='both', expand=True)

    tk.Label(
        card,
        text='مدیریت کاربران و دروس',
        bg=CARD,
        fg=TEXT,
        font=HEADER_FONT
    ).pack(pady=(20, 25))

    # ===== Buttons Grid =====
    btn_frame = tk.Frame(card, bg=CARD)
    btn_frame.pack()

    BTN_W = 18
    BTN_H = 2

    tk.Button(
        btn_frame,
        text='👨‍🏫 ثبت استاد',
        width=BTN_W,
        height=BTN_H,
        bg=PRIMARY,
        fg='white',
        font=NORMAL_FONT,
        relief='flat',
        cursor='hand2',
        command=teacher_form
    ).grid(row=0, column=0, padx=12, pady=10)

    tk.Button(
        btn_frame,
        text='📚 ثبت درس',
        width=BTN_W,
        height=BTN_H,
        bg=PRIMARY,
        fg='white',
        font=NORMAL_FONT,
        relief='flat',
        cursor='hand2',
        command=course_form
    ).grid(row=0, column=1, padx=12, pady=10)

    tk.Button(
        btn_frame,
        text='🎓 ثبت دانشجو',
        width=BTN_W,
        height=BTN_H,
        bg=SUCCESS,
        fg='white',
        font=NORMAL_FONT,
        relief='flat',
        cursor='hand2',
        command=student_form
    ).grid(row=1, column=0, padx=12, pady=10)

    tk.Button(
        btn_frame,
        text='🔗 تخصیص درس',
        width=BTN_W,
        height=BTN_H,
        bg='#7C3AED',
        fg='white',
        font=NORMAL_FONT,
        relief='flat',
        cursor='hand2',
        command=assign_form
    ).grid(row=1, column=1, padx=12, pady=10)

    tk.Button(
        btn_frame,
        text='🗑 حذف استاد',
        width=BTN_W,
        height=BTN_H,
        bg=DANGER,
        fg='white',
        font=NORMAL_FONT,
        relief='flat',
        cursor='hand2',
        command=delete_teacher_form
    ).grid(row=2, column=0, padx=12, pady=10)

    tk.Button(
        btn_frame,
        text='🗑 حذف درس',
        width=BTN_W,
        height=BTN_H,
        bg=DANGER,
        fg='white',
        font=NORMAL_FONT,
        relief='flat',
        cursor='hand2',
        command=delete_course_form
    ).grid(row=2, column=1, padx=12, pady=10)

    tk.Button(
        btn_frame,
        text='🗑 حذف دانشجو',
        width=BTN_W,
        height=BTN_H,
        bg=DANGER,
        fg='white',
        font=NORMAL_FONT,
        relief='flat',
        cursor='hand2',
        command=delete_student_form
    ).grid(row=3, column=0, columnspan=2, pady=14)

    # ===== Back Button =====
    tk.Button(
        card,
        text='⬅ بازگشت به ورود',
        width=20,
        height=2,
        bg='#64748B',
        fg='white',
        font=NORMAL_FONT,
        relief='flat',
        cursor='hand2',
        command=lambda: show_frame(login_frame)
    ).pack(pady=(25, 20))



def show_grade_form_list():

    for widget in teacher_frame.winfo_children():
        widget.destroy()

    tk.Label(
        teacher_frame,
        text="انتخاب درس برای ثبت نمره",
        font=("Arial",16)
    ).pack(pady=20)

    my_courses = [
        c for c, t in assignments.items()
        if t == current_teacher
    ]

    if not my_courses:
        tk.Label(
            teacher_frame,
            text="هیچ درسی ندارید.",
            fg="red"
        ).pack(pady=30)

    else:
        for code in my_courses:
            tk.Button(
                teacher_frame,
                text=f"{code} - {courses[code]['name']}",
                width=40,
                command=lambda c=code: show_grade_form(c)
            ).pack(pady=5)

    tk.Button(
        teacher_frame,
        text="بازگشت",
        command=setup_teacher_frame
    ).pack(pady=20)

def save_all_grades(course_code):
    if course_code not in grades:
        grades[course_code] = {}

    saved_count = 0

    for widget in teacher_frame.winfo_children():
        if isinstance(widget, tk.Frame):
            for child in widget.winfo_children():
                if isinstance(child, tk.Entry) and hasattr(child, "username"):
                    value = child.grade_var.get().strip()

                    if value == "":
                        continue

                    try:
                        grade = float(value)

                        if 0 <= grade <= 20:
                            grades[course_code][child.username] = str(grade)
                            saved_count += 1
                        else:
                            messagebox.showwarning(
                                "خطا",
                                f"نمره {child.username} باید بین ۰ تا ۲۰ باشد."
                            )
                    except ValueError:
                        messagebox.showwarning(
                            "خطا",
                            f"نمره {child.username} معتبر نیست."
                        )

    save_all_data()
    messagebox.showinfo("موفق", f"{saved_count} نمره ذخیره شد.")
def show_grade_form(course_code):
    for widget in teacher_frame.winfo_children():
        widget.destroy()

    tk.Label(teacher_frame, text=f"نمرات درس: {courses[course_code]['name']} ({course_code})",
             font=("Arial", 16)).pack(pady=20)

    if not students:
        tk.Label(teacher_frame, text="هیچ دانشجویی ثبت نشده!", fg="red").pack(pady=50)
    else:
        table_frame = tk.Frame(teacher_frame)
        table_frame.pack(pady=10)

        tk.Label(table_frame, text="کد", width=10, bg="lightgray").grid(row=0, column=0)
        tk.Label(table_frame, text="نام", width=25, bg="lightgray").grid(row=0, column=1)
        tk.Label(table_frame, text="نمره", width=10, bg="lightgray").grid(row=0, column=2)

        row = 1
        selected_students = [
            username
            for username, selected in student_selections.items()
            if course_code in selected
        ]

        for username in selected_students:
            info = students[username]
            tk.Label(table_frame, text=info["code"], width=10).grid(row=row, column=0)
            tk.Label(table_frame, text=f"{info['name']} {info['lname']}", width=25).grid(row=row, column=1)

            grade_var = tk.StringVar(value=grades.get(course_code, {}).get(username, ""))

            entry = tk.Entry(table_frame, textvariable=grade_var, width=10)
            entry.grid(row=row, column=2)

            entry.grade_var = grade_var
            entry.username = username
            row += 1

        tk.Label(teacher_frame, text="نمره (0-20) | Tab=ذخیره", fg="blue").pack(pady=10)

    tk.Button(teacher_frame, text="ثبت و بازگشت",
              command=lambda: [save_all_grades(course_code), setup_teacher_frame()],
              bg="green", fg="white", width=20, height=2).pack(pady=20)

def save_grade(u, var, c):
    g = var.get().strip()
    if not g: return
    try:
        grade = float(g)
        if 0 <= grade <= 20:
            if c not in grades: grades[c] = {}
            grades[c][u] = str(grade)
        else:
            messagebox.showwarning("خطا", "0-20")
            var.set("")
    except:
        messagebox.showerror("خطا", "عدد وارد کنید")
        var.set("")


def show_report_list():
    for widget in teacher_frame.winfo_children():
        widget.destroy()

    tk.Label(teacher_frame, text="گزارش نمرات", font=("Arial", 18)).pack(pady=20)

    my_courses = [c for c, t in assignments.items() if t == current_teacher]

    if not my_courses:
        tk.Label(teacher_frame, text="هیچ درسی ندارید.", fg="red").pack(pady=50)
    else:
        for course_code in my_courses:
            course_name = courses[course_code]["name"]
            tk.Label(teacher_frame, text=f"\n--- {course_code} - {course_name} ---",
                     font=("Arial", 14, "bold")).pack(anchor="w", padx=20)

            grades_list = []
            selected_students = [
                username
                for username, selected in student_selections.items()
                if course_code in selected
            ]

            for username in selected_students:
                info = students[username]
                grade = grades.get(course_code, {}).get(username, "-")
                tk.Label(teacher_frame, text=f"{info['code']} | {info['name']} {info['lname']}: {grade}",
                         anchor="w").pack(anchor="w", padx=40)

                if grade != "-" and grade.replace('.', '').isdigit():
                    grades_list.append(float(grade))

            if grades_list:
                max_g = max(grades_list)
                min_g = min(grades_list)
                tk.Label(teacher_frame, text=f"بالاترین: {max_g} | پایین‌ترین: {min_g}",
                         font=("Arial", 12, "bold"), fg="green").pack(anchor="w", padx=40)

    tk.Button(teacher_frame, text="بازگشت", command=setup_teacher_frame).pack(pady=20)
save_all_data()
def delete_teacher_form():

    for widget in admin_frame.winfo_children():
        widget.destroy()

    tk.Label(
        admin_frame,
        text="حذف استاد",
        bg=BG,
        fg=PRIMARY,
        font=TITLE_FONT
    ).pack(pady=20)

    if not teachers:
        tk.Label(
            admin_frame,
            text="هیچ استادی ثبت نشده است.",
            font=NORMAL_FONT,
            fg="red"
        ).pack(pady=30)

    else:

        card = tk.Frame(
            admin_frame,
            bg="white",
            bd=1,
            relief="solid"
        )
        card.pack(pady=10, ipadx=20, ipady=20)


        tk.Label(
            card,
            text="انتخاب استاد",
            bg="white",
            font=NORMAL_FONT
        ).grid(row=0,column=0,padx=10,pady=10)


        teacher_var = tk.StringVar()
        teacher_var.set(list(teachers.keys())[0])


        tk.OptionMenu(
            card,
            teacher_var,
            *teachers.keys()
        ).grid(row=0,column=1,padx=10,pady=10)


        def delete_teacher():

            username = teacher_var.get()

            answer = messagebox.askyesno(
                "تایید حذف",
                f"آیا مطمئن هستید استاد {username} حذف شود؟"
            )

            if answer:

                del teachers[username]


                # حذف تخصیص درس‌های استاد
                for course in list(assignments.keys()):
                    if assignments[course] == username:
                        del assignments[course]


                save_all_data()

                messagebox.showinfo(
                    "موفق",
                    "استاد حذف شد."
                )

                setup_admin_frame()


        modern_button(
            card,
            "🗑 حذف استاد",
            delete_teacher,
            DANGER
        ).grid(row=1,column=0,columnspan=2,pady=20)



    modern_button(
        admin_frame,
        "⬅ بازگشت",
        setup_admin_frame,
        DANGER
    ).pack(pady=15)
# ---------------- Teacher Form ----------------
def teacher_form():

    for widget in admin_frame.winfo_children():
        widget.destroy()

    tk.Label(
        admin_frame,
        text="ثبت استاد",
        bg=BG,
        fg=PRIMARY,
        font=TITLE_FONT
    ).pack(pady=20)

    card = tk.Frame(
        admin_frame,
        bg="white",
        bd=1,
        relief="solid"
    )
    card.pack(pady=10, ipadx=20, ipady=20)

    tk.Label(card, text="نام", bg="white", font=NORMAL_FONT).grid(row=0, column=0, padx=10, pady=10, sticky="e")
    tk.Label(card, text="نام خانوادگی", bg="white", font=NORMAL_FONT).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    tk.Label(card, text="نام کاربری", bg="white", font=NORMAL_FONT).grid(row=2, column=0, padx=10, pady=10, sticky="e")
    tk.Label(card, text="رمز عبور", bg="white", font=NORMAL_FONT).grid(row=3, column=0, padx=10, pady=10, sticky="e")

    name_entry = tk.Entry(card, width=30)
    lname_entry = tk.Entry(card, width=30)
    user_entry = tk.Entry(card, width=30)
    pass_entry = tk.Entry(card, width=30, show="*")

    name_entry.grid(row=0, column=1, padx=10, pady=10)
    lname_entry.grid(row=1, column=1, padx=10, pady=10)
    user_entry.grid(row=2, column=1, padx=10, pady=10)
    pass_entry.grid(row=3, column=1, padx=10, pady=10)

    def add_teacher():

        username = user_entry.get().strip()

        if username == "":
            messagebox.showerror("خطا", "نام کاربری وارد نشده است.")
            return

        if username in teachers:
            messagebox.showerror("خطا", "این استاد قبلاً ثبت شده است.")
            return

        teachers[username] = {
            "name": name_entry.get(),
            "lname": lname_entry.get(),
            "password": pass_entry.get()
        }

        save_all_data()

        messagebox.showinfo("موفق", "استاد با موفقیت ثبت شد.")

        setup_admin_frame()

    modern_button(
        card,
        "✅ ثبت استاد",
        add_teacher,
        SUCCESS
    ).grid(row=4, column=0, columnspan=2, pady=20)

    modern_button(
        admin_frame,
        "⬅ بازگشت",
        setup_admin_frame,
        DANGER
    ).pack(pady=15)
# ----- Course Form -----
def course_form():

    for widget in admin_frame.winfo_children():
        widget.destroy()

    tk.Label(
        admin_frame,
        text="ثبت درس",
        bg=BG,
        fg=PRIMARY,
        font=TITLE_FONT
    ).pack(pady=20)

    card = tk.Frame(
        admin_frame,
        bg="white",
        bd=1,
        relief="solid"
    )
    card.pack(pady=10, ipadx=20, ipady=20)

    tk.Label(card, text="کد درس", bg="white", font=NORMAL_FONT).grid(row=0, column=0, padx=10, pady=10, sticky="e")
    tk.Label(card, text="نام درس", bg="white", font=NORMAL_FONT).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    tk.Label(card, text="تعداد واحد", bg="white", font=NORMAL_FONT).grid(row=2, column=0, padx=10, pady=10, sticky="e")

    code_entry = tk.Entry(card, width=30)
    name_entry = tk.Entry(card, width=30)
    unit_entry = tk.Entry(card, width=30)

    code_entry.grid(row=0, column=1, padx=10, pady=10)
    name_entry.grid(row=1, column=1, padx=10, pady=10)
    unit_entry.grid(row=2, column=1, padx=10, pady=10)

    def add_course():

        code = code_entry.get().strip()

        if code == "":
            messagebox.showerror("خطا", "کد درس وارد نشده است.")
            return

        if code in courses:
            messagebox.showerror("خطا", "این درس قبلاً ثبت شده است.")
            return

        courses[code] = {
            "name": name_entry.get(),
            "unit": unit_entry.get()
        }

        save_all_data()

        messagebox.showinfo(
            "موفق",
            "درس با موفقیت ثبت شد."
        )

        setup_admin_frame()

    modern_button(
        card,
        "✅ ثبت درس",
        add_course,
        SUCCESS
    ).grid(row=3, column=0, columnspan=2, pady=20)

    modern_button(
        admin_frame,
        "⬅ بازگشت",
        setup_admin_frame,
        DANGER
    ).pack(pady=15)
def delete_course_form():

    for widget in admin_frame.winfo_children():
        widget.destroy()

    tk.Label(
        admin_frame,
        text="حذف درس",
        bg=BG,
        fg=PRIMARY,
        font=TITLE_FONT
    ).pack(pady=20)


    if not courses:

        tk.Label(
            admin_frame,
            text="هیچ درسی ثبت نشده است.",
            font=NORMAL_FONT,
            fg="red"
        ).pack(pady=30)

    else:

        card = tk.Frame(
            admin_frame,
            bg="white",
            bd=1,
            relief="solid"
        )

        card.pack(
            pady=10,
            ipadx=20,
            ipady=20
        )


        tk.Label(
            card,
            text="انتخاب درس",
            bg="white",
            font=NORMAL_FONT
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=10
        )


        course_var = tk.StringVar()
        course_var.set(list(courses.keys())[0])


        tk.OptionMenu(
            card,
            course_var,
            *courses.keys()
        ).grid(
            row=0,
            column=1,
            padx=10,
            pady=10
        )


        def delete_course():

            code = course_var.get()


            answer = messagebox.askyesno(
                "تایید حذف",
                f"آیا مطمئن هستید درس {code} حذف شود؟"
            )


            if answer:

                # حذف درس
                del courses[code]


                # حذف تخصیص استاد
                if code in assignments:
                    del assignments[code]


                # حذف نمرات درس
                if code in grades:
                    del grades[code]


                # حذف انتخاب واحد دانشجویان
                for student in student_selections:
                    if code in student_selections[student]:
                        student_selections[student].remove(code)


                save_all_data()


                messagebox.showinfo(
                    "موفق",
                    "درس با موفقیت حذف شد."
                )


                setup_admin_frame()



        modern_button(
            card,
            "🗑 حذف درس",
            delete_course,
            DANGER
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            pady=20
        )


    modern_button(
        admin_frame,
        "⬅ بازگشت",
        setup_admin_frame,
        DANGER
    ).pack(pady=15)

# ----- Assign Form -----
def assign_form():

    for widget in admin_frame.winfo_children():
        widget.destroy()

    tk.Label(
        admin_frame,
        text="تخصیص درس به استاد",
        bg=BG,
        fg=PRIMARY,
        font=TITLE_FONT
    ).pack(pady=20)

    if not courses:
        messagebox.showwarning("خطا", "ابتدا درس ثبت کنید.")
        setup_admin_frame()
        return

    if not teachers:
        messagebox.showwarning("خطا", "ابتدا استاد ثبت کنید.")
        setup_admin_frame()
        return

    card = tk.Frame(
        admin_frame,
        bg="white",
        bd=1,
        relief="solid"
    )
    card.pack(pady=10, ipadx=20, ipady=20)

    tk.Label(
        card,
        text="انتخاب درس",
        bg="white",
        font=NORMAL_FONT
    ).grid(row=0, column=0, padx=10, pady=10, sticky="e")

    tk.Label(
        card,
        text="انتخاب استاد",
        bg="white",
        font=NORMAL_FONT
    ).grid(row=1, column=0, padx=10, pady=10, sticky="e")

    course_var = tk.StringVar(value=list(courses.keys())[0])
    teacher_var = tk.StringVar(value=list(teachers.keys())[0])

    tk.OptionMenu(card, course_var, *courses.keys()).grid(
        row=0,
        column=1,
        padx=10,
        pady=10
    )

    tk.OptionMenu(card, teacher_var, *teachers.keys()).grid(
        row=1,
        column=1,
        padx=10,
        pady=10
    )

    def assign():

        course = course_var.get()
        teacher = teacher_var.get()

        if course in assignments:

            old_teacher = assignments[course]

            if old_teacher != teacher:

                answer = messagebox.askyesno(
                    "تغییر استاد",
                    f"این درس قبلاً به استاد «{old_teacher}» اختصاص داده شده است.\n\n"
                    "آیا مایل به جایگزینی هستید؟"
                )

                if not answer:
                    return

        assignments[course] = teacher

        save_all_data()

        messagebox.showinfo(
            "موفق",
            "تخصیص با موفقیت انجام شد."
        )

        setup_admin_frame()

    modern_button(
        card,
        "✅ ثبت تخصیص",
        assign,
        SUCCESS
    ).grid(row=2, column=0, columnspan=2, pady=20)

    modern_button(
        admin_frame,
        "⬅ بازگشت",
        setup_admin_frame,
        DANGER
    ).pack(pady=15)


# ----- Student Form -----
# ---------------- Student Form ----------------
def student_form():

    for widget in admin_frame.winfo_children():
        widget.destroy()

    tk.Label(
        admin_frame,
        text="ثبت دانشجو",
        bg=BG,
        fg=PRIMARY,
        font=TITLE_FONT
    ).pack(pady=20)

    card = tk.Frame(
        admin_frame,
        bg="white",
        bd=1,
        relief="solid"
    )
    card.pack(pady=10, ipadx=20, ipady=20)

    labels = [
        "کد دانشجویی",
        "نام",
        "نام خانوادگی",
        "نام کاربری",
        "رمز عبور"
    ]

    entries = []

    for i, text in enumerate(labels):
        tk.Label(
            card,
            text=text,
            bg="white",
            font=NORMAL_FONT
        ).grid(row=i, column=0, padx=10, pady=10, sticky="e")

        e = tk.Entry(card, width=30)

        if text == "رمز عبور":
            e.config(show="*")

        e.grid(row=i, column=1, padx=10, pady=10)
        entries.append(e)

    code_entry, name_entry, lname_entry, user_entry, pass_entry = entries

    def add_student():

        username = user_entry.get().strip()

        if username == "":
            messagebox.showerror(
                "خطا",
                "نام کاربری وارد نشده است."
            )
            return

        if username in students:
            messagebox.showerror(
                "خطا",
                "این نام کاربری قبلاً ثبت شده است."
            )
            return

        students[username] = {
            "code": code_entry.get().strip(),
            "name": name_entry.get().strip(),
            "lname": lname_entry.get().strip(),
            "password": pass_entry.get()
        }

        save_all_data()

        messagebox.showinfo(
            "موفق",
            "دانشجو با موفقیت ثبت شد."
        )

        setup_admin_frame()

    modern_button(
        card,
        "✅ ثبت دانشجو",
        add_student,
        SUCCESS
    ).grid(row=5, column=0, columnspan=2, pady=20)

    modern_button(
        admin_frame,
        "⬅ بازگشت",
        setup_admin_frame,
        DANGER
    ).pack(pady=15)
def delete_student_form():

    for widget in admin_frame.winfo_children():
        widget.destroy()


    tk.Label(
        admin_frame,
        text="حذف دانشجو",
        bg=BG,
        fg=PRIMARY,
        font=TITLE_FONT
    ).pack(pady=20)


    if not students:

        tk.Label(
            admin_frame,
            text="هیچ دانشجویی ثبت نشده است.",
            font=NORMAL_FONT,
            fg="red"
        ).pack(pady=30)


    else:

        card = tk.Frame(
            admin_frame,
            bg="white",
            bd=1,
            relief="solid"
        )

        card.pack(
            pady=10,
            ipadx=20,
            ipady=20
        )


        tk.Label(
            card,
            text="انتخاب دانشجو",
            bg="white",
            font=NORMAL_FONT
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=10
        )


        student_var = tk.StringVar()
        student_var.set(list(students.keys())[0])


        tk.OptionMenu(
            card,
            student_var,
            *students.keys()
        ).grid(
            row=0,
            column=1,
            padx=10,
            pady=10
        )


        def delete_student():

            username = student_var.get()


            answer = messagebox.askyesno(
                "تایید حذف",
                f"آیا مطمئن هستید دانشجو {username} حذف شود؟"
            )


            if answer:


                # حذف دانشجو
                del students[username]


                # حذف انتخاب واحد
                if username in student_selections:
                    del student_selections[username]


                # حذف نمرات دانشجو
                for course in list(grades.keys()):
                    if username in grades[course]:
                        del grades[course][username]


                save_all_data()


                messagebox.showinfo(
                    "موفق",
                    "دانشجو با موفقیت حذف شد."
                )


                setup_admin_frame()



        modern_button(
            card,
            "🗑 حذف دانشجو",
            delete_student,
            DANGER
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            pady=20
        )


    modern_button(
        admin_frame,
        "⬅ بازگشت",
        setup_admin_frame,
        DANGER
    ).pack(pady=15)
# ---------------- Teacher Panel ----------------
current_teacher = None  # متغیر جهانی برای ذخیره نام کاربری استاد لاگین شده


def setup_teacher_frame():
    if current_teacher is None or current_teacher not in teachers:
        show_frame(login_frame)
        return

    for widget in teacher_frame.winfo_children():
        widget.destroy()

    teacher_info = teachers[current_teacher]
    tk.Label(teacher_frame, text=f"خوش آمدید استاد {teacher_info['name']} {teacher_info['lname']}",
             font=("Arial", 16), fg="darkblue").pack(pady=20)

    btn_frame = tk.Frame(teacher_frame)
    btn_frame.pack(pady=20)

    tk.Button(btn_frame, text="ثبت نمره", width=20, height=2,
              command=show_grade_form_list,
              bg="lightgreen").grid(row=0, column=0, padx=20, pady=10)

    tk.Button(btn_frame, text="گزارش نمرات", width=20, height=2,
              command=show_report_list,
              bg="lightblue").grid(row=0, column=1, padx=20, pady=10)

    tk.Button(teacher_frame, text="خروج", command=lambda: show_frame(login_frame),
              bg="gray", fg="white", width=20).pack(pady=30)
def show_grade_form_list():

    for widget in teacher_frame.winfo_children():
        widget.destroy()

    tk.Label(
        teacher_frame,
        text="انتخاب درس برای ثبت نمره",
        font=("Arial",16)
    ).pack(pady=20)

    my_courses = [
        c for c, t in assignments.items()
        if t == current_teacher
    ]

    if not my_courses:
        tk.Label(
            teacher_frame,
            text="هیچ درسی به شما اختصاص داده نشده است.",
            fg="red"
        ).pack(pady=20)

    else:
        for code in my_courses:
            tk.Button(
                teacher_frame,
                text=f"{code} - {courses[code]['name']}",
                width=40,
                command=lambda c=code: show_grade_form(c)
            ).pack(pady=5)

    tk.Button(
        teacher_frame,
        text="بازگشت",
        command=setup_teacher_frame
    ).pack(pady=20)

def setup_teacher_report_frame():
    for widget in teacher_report_frame.winfo_children():
        widget.destroy()
    tk.Label(teacher_report_frame, text="گزارش نمرات", font=("Arial", 18)).pack(pady=50)
    tk.Button(teacher_report_frame, text="بازگشت",
              command=lambda: [setup_teacher_frame(), show_frame(teacher_frame)]).pack(pady=20)


# ---------------- Student Panel ----------------
current_student = None  # برای دانشجوی لاگین شده

def setup_teacher_grade_frame():
    for widget in teacher_grade_frame.winfo_children():
        widget.destroy()
    tk.Label(teacher_grade_frame, text="ثبت نمره", font=("Arial", 18)).pack(pady=20)
    my_courses = [c for c, t in assignments.items() if t == current_teacher]
    if not my_courses:
        tk.Label(teacher_grade_frame, text="هیچ درسی به شما اختصاص داده نشده است.", font=("Arial", 14), fg="red").pack(pady=50)
    else:
        tk.Label(teacher_grade_frame, text="دروس شما:", font=("Arial", 14)).pack(pady=10)
        course_frame = tk.Frame(teacher_grade_frame)
        course_frame.pack(pady=10)
        for code in my_courses:
            name = courses[code]["name"]
            btn = tk.Button(course_frame, text=f"{code} - {name}", width=40, height=2,
                           command=lambda c=code: show_student_grades(c))
            btn.pack(pady=5)
    tk.Button(teacher_grade_frame, text="بازگشت", command=lambda: [setup_teacher_frame(), show_frame(teacher_frame)]).pack(pady=20)

def show_student_grades(course_code):
    for widget in teacher_grade_frame.winfo_children():
        widget.destroy()
    tk.Label(teacher_grade_frame, text=f"نمرات درس: {courses[course_code]['name']} ({course_code})", font=("Arial", 16)).pack(pady=20)
    # Treeview table code here (کوتاه شده برای نمایش)
    # ... (کد کامل Treeview از پاسخ قبلی)
    tk.Button(teacher_frame, text="بازگشت", command=setup_teacher_frame).pack(pady=20)

# بقیه توابع teacher_report_frame و student...


def setup_student_frame():
    global current_student
    for widget in student_frame.winfo_children():
        widget.destroy()

    tk.Label(student_frame,
             text=f"پنل دانشجو: {students[current_student]['name']} {students[current_student]['lname']}",
             font=("Arial", 16)).pack(pady=20)

    btn_frame = tk.Frame(student_frame)
    btn_frame.pack(pady=20)

    tk.Button(btn_frame, text="انتخاب واحد", width=20, height=2,
              command=select_courses_form, bg="lightgreen").grid(row=0, column=0, padx=20)

    tk.Button(btn_frame, text="نمایش کارنامه", width=20, height=2,
              command=show_report_card, bg="lightblue").grid(row=0, column=1, padx=20)

    tk.Button(student_frame, text="خروج", command=lambda: show_frame(login_frame),
              bg="gray", fg="white", width=20).pack(pady=30)



def select_courses_form():
    for widget in student_frame.winfo_children():
        widget.destroy()

    tk.Label(student_frame, text="انتخاب واحد", font=("Arial", 16)).pack(pady=20)

    if not courses:
        tk.Label(student_frame, text="هنوز درسی ثبت نشده است.").pack(pady=20)
    else:
        selected = student_selections.get(current_student, [])

        for code, info in courses.items():
            var = tk.IntVar(value=1 if code in selected else 0)

            chk = tk.Checkbutton(student_frame, text=f"{code} - {info['name']} ({info['unit']} واحد)",
                                 variable=var)
            chk.var = var  # برای دسترسی بعدی
            chk.code = code
            chk.pack(anchor="w", padx=50, pady=2)

        def save_selection():
            new_selected = []
            for widget in student_frame.winfo_children():
                if isinstance(widget, tk.Checkbutton) and hasattr(widget, 'code'):
                    if widget.var.get() == 1:
                        new_selected.append(widget.code)
            student_selections[current_student] = new_selected
            save_all_data()
            messagebox.showinfo("موفق", "واحدها با موفقیت ذخیره شدند")
        tk.Button(student_frame, text="ذخیره انتخاب واحد", command=save_selection, bg="green", fg="white").pack(pady=20)


    tk.Button(student_frame, text="بازگشت", command=setup_student_frame).pack()


# نمایش کارنامه
def back_to_student_menu():
    setup_student_frame()  # هر منویی که داری

    # ===== Backup PDF =====
    # def generate_report_pdf_backup():
    #     ...

def generate_report_pdf():
    preview = messagebox.askyesno(
        "پیش‌نمایش کارنامه",
        "آیا می‌خواهید ابتدا کارنامه را مشاهده کنید؟"
    )
    if preview:
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        )

        temp_path = temp_file.name
        temp_file.close()

        file_path = temp_path

    else:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile=f"Report_{students[current_student]['code']}.pdf",
            title="محل ذخیره کارنامه را انتخاب کنید"
        )

        if not file_path:
            return


    if not file_path:
        return

    pdf = canvas.Canvas(file_path, pagesize=A4)

    width, height = A4

    student = students[current_student]

    report_number = f"RC-{student['code']}-{jdatetime.datetime.now().strftime('%Y%m%d')}"

    report_date = jdatetime.datetime.now().strftime("%Y/%m/%d")

    # ---------------- Page Border ----------------

    pdf.setLineWidth(1)
    pdf.rect(
        35,
        35,
        width - 70,
        height - 70
    )

    # تاریخ صدور کارنامه


    pdf.setFont("Vazir", 10)

        # ---------------- Header ----------------
    pdf.setLineWidth(2)
    pdf.line(50, height-80, width-50, height-80)

    pdf.setFont("Vazir", 18)
    pdf.drawCentredString(
    width/2,
    height-60,
    fa("سیستم مدیریت دانشگاه")
)

    pdf.setFont("Vazir", 15)
    pdf.drawCentredString(
        width/2,
        height-100,
        fa("کارنامه تحصیلی دانشجو")
    )

    pdf.line(50, height-120, width-50, height-120)


    # ---------------- Student Info ----------------

    y = height - 160

    pdf.setFont("Vazir", 12)

    pdf.drawRightString(
        width - 60,
        y,
        fa(f"کد دانشجویی : {student['code']}")
    )

    pdf.drawRightString(
        width - 60,
        y - 25,
        fa(f"نام و نام خانوادگی : {student['name']} {student['lname']}")
    )

    pdf.drawRightString(
        width - 60,
        y - 50,
        fa(f"نام کاربری : {current_student}")
    )

    pdf.drawRightString(
        width - 60,
        y - 75,
        fa(f"شماره کارنامه : {report_number}")
    )

    pdf.drawRightString(
        width - 60,
        y - 100,
        fa(f"تاریخ صدور : {report_date}")
    )

    # ---------------- Table ----------------

    y -= 100

    headers = [
        "کد درس",
        "نام درس",
        "واحد",
        "نمره",
        "وضعیت"
    ]

    x_positions = [520, 400, 300, 220, 120]

    pdf.setFont("Vazir", 11)

    # Header background
    pdf.setFillColorRGB(0.12, 0.31, 0.48)

    pdf.rect(
        50,
        y - 8,
        width - 100,
        25,
        fill=1,
        stroke=0
    )

    pdf.setFillColorRGB(1, 1, 1)

    for i, h in enumerate(headers):
        pdf.drawRightString(
            x_positions[i],
            y,
            fa(h)
        )

    pdf.setFillColorRGB(0, 0, 0)

    pdf.line(50, y-5, width-50, y-5)

    y -= 30
    row_height = 22

    col_widths = [
        70,  # کد درس
        170,  # نام درس
        50,  # واحد
        60,  # نمره
        90  # وضعیت
    ]

    total_units = 0
    total_points = 0

    pdf.setFont("Vazir", 10)

    selected_courses = student_selections.get(
        current_student,
        []
    )


    for code in selected_courses:

        if code not in courses:
            continue

        info = courses[code]

        grade_str = grades.get(
            code,
            {}
        ).get(
            current_student,
            "-"
        )

        try:
            grade = float(grade_str)
        except:
            grade = None


        if grade is not None:
            status = "قبول" if grade >= 10 else "مردود"

            units = int(info["unit"])

            total_units += units
            total_points += grade * units

        else:
            status = "ثبت نشده"

        pdf.drawRightString(
            x_positions[0],
            y,
            code
        )

        pdf.drawRightString(
            x_positions[1],
            y,
            fa(info["name"])
        )

        pdf.drawRightString(
            x_positions[2],
            y,
            str(info["unit"])
        )

        pdf.drawRightString(
            x_positions[3],
            y,
            grade_str
        )

        # رنگ وضعیت
        if status == "قبول":
            pdf.setFillColor(colors.green)

        elif status == "مردود":
            pdf.setFillColor(colors.red)

        else:
            pdf.setFillColor(colors.gray)

        pdf.drawRightString(
            x_positions[4],
            y,
            fa(status)
        )

        # برگرداندن رنگ به مشکی
        pdf.setFillColor(colors.black)


        y -= 20


    # ---------------- Average ----------------

    if total_units > 0:
        average = total_points / total_units
    else:
        average = 0


    y -= 20

    pdf.line(
        50,
        y,
        width-50,
        y
    )

    pdf.setFont(
        "Vazir",
        13
    )

    pdf.drawRightString(
    width-60,
    y-30,
    fa(f"معدل کل : {average:.2f}")
)


    if average >= 10:
        final_status = "قبول"
    else:
        final_status = "مردود"

    pdf.drawRightString(
        width - 60,
        y - 55,
        fa(f"وضعیت تحصیلی : {final_status}")
    )

    # ---------------- Signature ----------------

    pdf.line(
        width - 220,
        80,
        width - 80,
        80
    )

    pdf.setFont(
        "Vazir",
        10
    )

    pdf.drawCentredString(
        width - 150,
        60,
        fa("امضاء و مهر اداره آموزش")    )

    # ---------------- Footer ----------------

    pdf.setStrokeColorRGB(0.75, 0.75, 0.75)

    pdf.line(
        50,
        45,
        width - 50,
        45
    )

    pdf.setFont(
        "Vazir",
        8
    )

    pdf.setFillColorRGB(
        0.45,
        0.45,
        0.45
    )

    pdf.drawCentredString(
        width / 2,
        28,
        fa("سیستم مدیریت دانشگاه | نسخه 1.0")
    )

    pdf.setFillColorRGB(
        0,
        0,
        0
    )

    pdf.save()

    webbrowser.open(file_path)


    messagebox.showinfo(
        "موفق",
        "کارنامه PDF ایجاد شد."
    )

def show_report_card():
    for widget in student_frame.winfo_children():
        widget.destroy()

    tk.Label(
        student_frame,
        text="📄 کارنامه تحصیلی دانشجو",
        font=("Arial", 20, "bold"),
        fg="#1E3A8A"
    ).pack(pady=20)

    selected_courses = student_selections.get(current_student, [])
    # ===== اطلاعات دانشجو =====
    student_info_frame = tk.Frame(
        student_frame,
        bg="white",
        bd=2,
        relief="solid"
    )
    student_info_frame.pack(pady=10, padx=30, fill="x")

    student = students[current_student]

    tk.Label(
        student_info_frame,
        text=f"نام دانشجو: {student['name']} {student['lname']}",
        font=("Arial", 13, "bold"),
        bg="white"
    ).pack(pady=5)

    tk.Label(
        student_info_frame,
        text=f"کد دانشجویی: {student['code']}",
        font=("Arial", 12),
        bg="white"
    ).pack(pady=5)
    if not selected_courses:
        tk.Label(student_frame, text="شما هیچ واحدی انتخاب نکرده‌اید.").pack(pady=30)
    else:
        total_units = 0
        total_grade_points = 0

        frame = tk.Frame(
            student_frame,
            bg="white",
            bd=2,
            relief="solid"
        )
        frame.pack(pady=10, padx=30)

        headers = [
            "کد درس",
            "نام درس",
            "واحد",
            "نمره",
            "وضعیت"
        ]

        for col, title in enumerate(headers):
            tk.Label(
                frame,
                text=title,
                width=12,
                bg="#1F4E79",
                fg="white",
                font=("Arial", 11, "bold")
            ).grid(
                row=0,
                column=col,
                padx=1,
                pady=1
            )


        row = 1
        for code in selected_courses:
            if code not in courses:
                continue
            info = courses[code]
            grade_str = grades.get(code, {}).get(current_student, "-")
            try:
                grade = float(grade_str) if grade_str != "-" else None
            except:
                grade = None

            tk.Label(frame, text=code).grid(row=row, column=0)
            tk.Label(frame, text=info["name"]).grid(row=row, column=1)
            tk.Label(frame, text=info["unit"]).grid(row=row, column=2)
            tk.Label(frame, text=grade_str).grid(row=row, column=3)
            # وضعیت نمره
            if grade is not None:
                if grade >= 10:
                    status = "قبول"
                    color = "green"
                else:
                    status = "مردود"
                    color = "red"
            else:
                status = "ثبت نشده"
                color = "gray"

            tk.Label(
                frame,
                text=status,
                fg=color,
                font=("Arial", 10, "bold")
            ).grid(row=row, column=4)
            if grade is not None:
                status = "قبول" if grade >= 10 else "مردود"
            else:
                status = "-"

            tk.Label(
                frame,
                text=status,
                fg="green" if status == "قبول" else "red"
            ).grid(row=row, column=4)
            if grade is not None:
                units = int(info["unit"])
                total_units += units
                total_grade_points += grade * units

            row += 1

        if total_units > 0:
            average = total_grade_points / total_units
            tk.Label(student_frame, text=f"معدل: {average:.2f}", font=("Arial", 14, "bold"), fg="blue").pack(pady=20)
        else:
            tk.Label(student_frame, text="معدل: محاسبه نشده (نمره‌ای ثبت نشده)", fg="orange").pack(pady=20)
    tk.Button(
        student_frame,
        text="دانلود PDF کارنامه",
        command=generate_report_pdf,
        bg="green",
        fg="white",
        width=20
    ).pack(pady=10)
    tk.Button(student_frame, text="بازگشت", command=setup_student_frame).pack(pady=20)
#  دکمه برگشت (بالای همه چیز یا پایین)
back_btn = tk.Button(student_frame, text="🔙 بازگشت به منو",
                     font=("Arial", 12, "bold"),
                     bg="lightcoral", fg="white",
                     command=lambda: clear_window(),  #  برمیگرده به منوی دانشجو
                     width=15, height=1)
back_btn.pack(pady=20)

back_btn.pack(side=tk.TOP, pady=(0,10))  # بالای کارنامه



# ---------------- Start ----------------
# setup_admin_frame()
# setup_teacher_frame()
# setup_student_frame()

show_frame(login_frame)
root.mainloop()


import os
from datetime import datetime, timedelta

import mysql.connector

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "college-management-secret-key"
)


## =========================================================
# DATABASE CONNECTION - AIVEN MYSQL
# =========================================================

def get_db():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        port=int(os.environ.get("DB_PORT", "14254")),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME", "defaultdb"),
        ssl_disabled=False
    )
# =========================================================
# NO CACHE
# =========================================================

@app.after_request
def add_no_cache(response):

    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, max-age=0"
    )

    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template("home.html")


# =========================================================
# SIGN IN / REGISTRATION
# =========================================================

@app.route("/signin", methods=["GET", "POST"])
def signin():

    if request.method == "POST":

        role = request.form.get("role")

        username = request.form.get("username")
        password = request.form.get("password")

        # =================================================
        # STUDENT REGISTRATION
        # =================================================

        if role == "student":

            roll_no = request.form.get("roll_no")
            name = request.form.get("name")
            department = request.form.get("department")
            year = request.form.get("year")
            division = request.form.get("division")

            db = None
            cursor = None

            try:

                db = get_db()
                cursor = db.cursor()

                cursor.execute("""
                    INSERT INTO students
                    (
                        roll_no,
                        name,
                        department,
                        year,
                        division,
                        username,
                        password
                    )
                    VALUES
                    (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    roll_no,
                    name,
                    department,
                    year,
                    division,
                    username,
                    password
                ))

                db.commit()

                return """
                <h2>Student Registration Successful!</h2>
                <br>
                <a href="/login">Go to Login</a>
                """

            except Exception as e:

                if db:
                    db.rollback()

                return f"""
                <h2>Student Registration Error</h2>
                <p>{e}</p>
                <br>
                <a href="/signin">Go Back</a>
                """

            finally:

                if cursor:
                    cursor.close()

                if db:
                    db.close()


        # =================================================
        # FACULTY REGISTRATION
        # =================================================

        elif role == "faculty":

            faculty_name = request.form.get("faculty_name")
            department_name = request.form.get("department_name")
            subject_name = request.form.get("subject_name")
            qualification = request.form.get("qualification")
            designation = request.form.get("designation")
            email = request.form.get("email")
            mobile_number = request.form.get("mobile_number")

            db = None
            cursor = None

            try:

                db = get_db()
                cursor = db.cursor()

                cursor.execute("""
                    INSERT INTO faculty_registration
                    (
                        faculty_name,
                        department_name,
                        subject_name,
                        qualification,
                        designation,
                        email,
                        mobile_number,
                        username,
                        password
                    )
                    VALUES
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    faculty_name,
                    department_name,
                    subject_name,
                    qualification,
                    designation,
                    email,
                    mobile_number,
                    username,
                    password
                ))

                db.commit()

                return """
                <h2>Faculty Registration Successful!</h2>
                <br>
                <a href="/login">Go to Login</a>
                """

            except Exception as e:

                if db:
                    db.rollback()

                return f"""
                <h2>Faculty Registration Error</h2>
                <p>{e}</p>
                <br>
                <a href="/signin">Go Back</a>
                """

            finally:

                if cursor:
                    cursor.close()

                if db:
                    db.close()


        # =================================================
        # ADMIN REGISTRATION
        # =================================================

        elif role == "admin":

            admin_name = request.form.get("admin_name")
            email = request.form.get("admin_email")

            db = None
            cursor = None

            try:

                db = get_db()
                cursor = db.cursor()

                cursor.execute("""
                    INSERT INTO administrator
                    (
                        admin_name,
                        email,
                        username,
                        password
                    )
                    VALUES
                    (%s, %s, %s, %s)
                """, (
                    admin_name,
                    email,
                    username,
                    password
                ))

                db.commit()

                return """
                <h2>Administrator Registration Successful!</h2>
                <br>
                <a href="/login">Go to Login</a>
                """

            except Exception as e:

                if db:
                    db.rollback()

                return f"""
                <h2>Administrator Registration Error</h2>
                <p>{e}</p>
                <br>
                <a href="/signin">Go Back</a>
                """

            finally:

                if cursor:
                    cursor.close()

                if db:
                    db.close()


        # =================================================
        # HOD REGISTRATION
        # =================================================

        elif role == "hod":

            hod_name = request.form.get("hod_name")
            department_name = request.form.get("hod_department")
            email = request.form.get("hod_email")
            mobile_number = request.form.get("hod_mobile")

            db = None
            cursor = None

            try:

                db = get_db()
                cursor = db.cursor()

                cursor.execute("""
                    INSERT INTO department_hod
                    (
                        hod_name,
                        department_name,
                        email,
                        mobile_number,
                        username,
                        password
                    )
                    VALUES
                    (%s, %s, %s, %s, %s, %s)
                """, (
                    hod_name,
                    department_name,
                    email,
                    mobile_number,
                    username,
                    password
                ))

                db.commit()

                return """
                <h2>HOD Registration Successful!</h2>
                <br>
                <a href="/login">Go to Login</a>
                """

            except Exception as e:

                if db:
                    db.rollback()

                return f"""
                <h2>HOD Registration Error</h2>
                <p>{e}</p>
                <br>
                <a href="/signin">Go Back</a>
                """

            finally:

                if cursor:
                    cursor.close()

                if db:
                    db.close()


        # =================================================
        # LIBRARIAN REGISTRATION
        # =================================================

        elif role == "librarian":

            librarian_name = request.form.get("librarian_name")
            email = request.form.get("librarian_email")
            mobile_number = request.form.get("librarian_mobile")

            db = None
            cursor = None

            try:

                db = get_db()
                cursor = db.cursor()

                cursor.execute("""
                    INSERT INTO librarian
                    (
                        librarian_name,
                        email,
                        mobile_number,
                        username,
                        password
                    )
                    VALUES
                    (%s, %s, %s, %s, %s)
                """, (
                    librarian_name,
                    email,
                    mobile_number,
                    username,
                    password
                ))

                db.commit()

                return """
                <h2>Librarian Registration Successful!</h2>
                <br>
                <a href="/login">Go to Login</a>
                """

            except Exception as e:

                if db:
                    db.rollback()

                return f"""
                <h2>Librarian Registration Error</h2>
                <p>{e}</p>
                <br>
                <a href="/signin">Go Back</a>
                """

            finally:

                if cursor:
                    cursor.close()

                if db:
                    db.close()


        return "Invalid Role"

    return render_template("signin.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        role = request.form.get("role")

        username = request.form.get("username")
        password = request.form.get("password")

        db = None
        cursor = None

        try:

            db = get_db()
            cursor = db.cursor()

            # =================================================
            # STUDENT LOGIN
            # =================================================

            if role == "student":

                cursor.execute("""
                    SELECT
                        student_id,
                        name,
                        department,
                        year,
                        division
                    FROM students
                    WHERE username = %s
                    AND password = %s
                """, (
                    username,
                    password
                ))

                user = cursor.fetchone()

                if user:

                    session.clear()

                    session["role"] = "student"
                    session["student_id"] = user[0]
                    session["student_name"] = user[1]
                    session["department"] = user[2]
                    session["year"] = user[3]
                    session["division"] = user[4]

                    return redirect(url_for("dashboard"))

                return "Invalid Student Username or Password"


            # =================================================
            # FACULTY LOGIN
            # =================================================

            elif role == "faculty":

                cursor.execute("""
                    SELECT
                        faculty_id,
                        faculty_name,
                        department_name,
                        subject_name
                    FROM faculty_registration
                    WHERE username = %s
                    AND password = %s
                """, (
                    username,
                    password
                ))

                user = cursor.fetchone()

                if user:

                    session.clear()

                    session["role"] = "faculty"
                    session["faculty_id"] = user[0]
                    session["faculty_name"] = user[1]
                    session["department"] = user[2]
                    session["subject"] = user[3]

                    return redirect(url_for("faculty_dashboard"))

                return "Invalid Faculty Username or Password"


            # =================================================
            # ADMIN LOGIN
            # =================================================

            elif role == "admin":

                cursor.execute("""
                    SELECT
                        admin_id,
                        admin_name
                    FROM administrator
                    WHERE username = %s
                    AND password = %s
                """, (
                    username,
                    password
                ))

                user = cursor.fetchone()

                if user:

                    session.clear()

                    session["role"] = "admin"
                    session["admin_id"] = user[0]
                    session["admin_name"] = user[1]

                    return redirect(url_for("admin_dashboard"))

                return "Invalid Administrator Username or Password"


            # =================================================
            # HOD LOGIN
            # =================================================

            elif role == "hod":

                cursor.execute("""
                    SELECT
                        hod_id,
                        hod_name,
                        department_name
                    FROM department_hod
                    WHERE username = %s
                    AND password = %s
                """, (
                    username,
                    password
                ))

                user = cursor.fetchone()

                if user:

                    session.clear()

                    session["role"] = "hod"
                    session["hod_id"] = user[0]
                    session["hod_name"] = user[1]
                    session["department"] = user[2]

                    return redirect(url_for("hod_dashboard"))

                return "Invalid HOD Username or Password"


            # =================================================
            # LIBRARIAN LOGIN
            # =================================================

            elif role == "librarian":

                cursor.execute("""
                    SELECT
                        librarian_id,
                        librarian_name
                    FROM librarian
                    WHERE username = %s
                    AND password = %s
                """, (
                    username,
                    password
                ))

                user = cursor.fetchone()

                if user:

                    session.clear()

                    session["role"] = "librarian"
                    session["librarian_id"] = user[0]
                    session["librarian_name"] = user[1]

                    return redirect(url_for("librarian_dashboard"))

                return "Invalid Librarian Username or Password"


            return "Invalid Role"

        except Exception as e:

            if db:
                db.rollback()

            return f"""
            <h2>Database Error</h2>
            <p>{e}</p>
            <br>
            <a href="/login">Go Back</a>
            """

        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()

    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if session.get("role") != "student":

        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        student_name=session.get("student_name")
    )


# =========================================================
# STUDENT / FACULTY / HOD / ADMIN ATTENDANCE
# =========================================================

@app.route("/student_attendance")
def student_attendance():

    role = session.get("role")

    if role not in [
        "student",
        "faculty",
        "admin",
        "hod"
    ]:

        return redirect(url_for("login"))

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        # =====================================================
        # STUDENT
        # =====================================================

        if role == "student":

            student_id = session.get("student_id")

            cursor.execute("""
                SELECT
                    sa.attendance_date,
                    sa.lecture_number,
                    sa.subject_name,
                    s.roll_no,
                    s.name,
                    s.department,
                    s.year,
                    s.division,
                    f.faculty_name,
                    sa.status
                FROM student_attendance sa
                INNER JOIN students s
                    ON sa.student_id = s.student_id
                LEFT JOIN faculty_registration f
                    ON sa.faculty_id = f.faculty_id
                WHERE sa.student_id = %s
                ORDER BY
                    sa.attendance_date DESC,
                    sa.lecture_number DESC
            """, (student_id,))

            attendance_data = cursor.fetchall()

            return render_template(
                "student_attendance.html",
                attendance_data=attendance_data,
                user_role="student"
            )


        # =====================================================
        # FACULTY
        # =====================================================

        if role == "faculty":

            faculty_id = session.get("faculty_id")

            cursor.execute("""
                SELECT
                    sa.attendance_date,
                    sa.lecture_number,
                    sa.subject_name,
                    s.roll_no,
                    s.name,
                    s.department,
                    s.year,
                    s.division,
                    f.faculty_name,
                    sa.status
                FROM student_attendance sa
                INNER JOIN students s
                    ON sa.student_id = s.student_id
                LEFT JOIN faculty_registration f
                    ON sa.faculty_id = f.faculty_id
                WHERE sa.faculty_id = %s
                ORDER BY
                    sa.attendance_date DESC,
                    sa.lecture_number DESC
            """, (faculty_id,))

            attendance_data = cursor.fetchall()

            return render_template(
                "student_attendance.html",
                attendance_data=attendance_data,
                user_role="faculty"
            )


        # =====================================================
        # HOD
        # =====================================================

        if role == "hod":

            department = session.get("department")

            cursor.execute("""
                SELECT
                    sa.attendance_date,
                    sa.lecture_number,
                    sa.subject_name,
                    s.roll_no,
                    s.name,
                    s.department,
                    s.year,
                    s.division,
                    f.faculty_name,
                    sa.status
                FROM student_attendance sa
                INNER JOIN students s
                    ON sa.student_id = s.student_id
                LEFT JOIN faculty_registration f
                    ON sa.faculty_id = f.faculty_id
                WHERE s.department = %s
                ORDER BY
                    sa.attendance_date DESC,
                    sa.lecture_number DESC
            """, (department,))

            attendance_data = cursor.fetchall()

            return render_template(
                "student_attendance.html",
                attendance_data=attendance_data,
                user_role="hod"
            )


        # =====================================================
        # ADMIN
        # =====================================================

        cursor.execute("""
            SELECT
                sa.attendance_date,
                sa.lecture_number,
                sa.subject_name,
                s.roll_no,
                s.name,
                s.department,
                s.year,
                s.division,
                f.faculty_name,
                sa.status
            FROM student_attendance sa
            INNER JOIN students s
                ON sa.student_id = s.student_id
            LEFT JOIN faculty_registration f
                ON sa.faculty_id = f.faculty_id
            ORDER BY
                sa.attendance_date DESC,
                sa.lecture_number DESC
        """)

        attendance_data = cursor.fetchall()

        return render_template(
            "student_attendance.html",
            attendance_data=attendance_data,
            user_role="admin"
        )

    except Exception as e:

        return f"""
        <h2>Attendance Error</h2>
        <p>{e}</p>
        <br>
        <a href="/dashboard">Go Back</a>
        """

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# STUDENT - MY ATTENDANCE
# =========================================================

@app.route("/my_attendance")
def my_attendance():

    if session.get("role") != "student":

        return redirect(url_for("login"))

    student_id = session.get("student_id")

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                sa.attendance_date,
                sa.lecture_number,
                sa.subject_name,
                f.faculty_name,
                sa.status
            FROM student_attendance sa
            LEFT JOIN faculty_registration f
                ON sa.faculty_id = f.faculty_id
            WHERE sa.student_id = %s
            ORDER BY
                sa.attendance_date DESC,
                sa.lecture_number DESC
        """, (student_id,))

        attendance = cursor.fetchall()

        return render_template(
            "my_attendance.html",
            attendance=attendance
        )

    except Exception as e:

        return f"""
        <h2>My Attendance Error</h2>
        <p>{e}</p>
        """

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# STUDENT - MY BOOKS
# =========================================================

@app.route("/my_books")
def my_books():

    if session.get("role") != "student":

        return redirect(url_for("login"))

    student_id = session.get("student_id")

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                lb.book_name,
                lb.author,
                li.issue_date,
                li.return_date,
                li.actual_return_date,
                li.status
            FROM library_issues li
            INNER JOIN library_books lb
                ON li.book_id = lb.book_id
            WHERE li.student_id = %s
            ORDER BY li.issue_date DESC
        """, (student_id,))

        books = cursor.fetchall()

        return render_template(
            "my_books.html",
            books=books
        )

    except Exception as e:

        return f"""
        <h2>My Books Error</h2>
        <p>{e}</p>
        """

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# STUDENT - FEES
# =========================================================

@app.route("/fees")
def fees():

    if session.get("role") != "student":

        return redirect(url_for("login"))

    student_id = session.get("student_id")

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                fee_type,
                amount,
                due_date,
                status
            FROM fees
            WHERE student_id = %s
            ORDER BY due_date
        """, (student_id,))

        fee_data = cursor.fetchall()

        return render_template(
            "fees.html",
            fee_data=fee_data
        )

    except Exception as e:

        return f"""
        <h2>Fees Error</h2>
        <p>{e}</p>
        """

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# NOTICES
# =========================================================

@app.route("/notices")
def notices():

    role = session.get("role")

    if role not in [
        "student",
        "faculty",
        "admin",
        "hod"
    ]:

        return redirect(url_for("login"))

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                notice_id,
                title,
                notice_text,
                created_at
            FROM notices
            ORDER BY created_at DESC
        """)

        notice_data = cursor.fetchall()

        return render_template(
            "notices.html",
            notice_data=notice_data,
            user_role=role
        )

    except Exception as e:

        return f"""
        <h2>Notice Error</h2>
        <p>{e}</p>
        """

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# FACULTY DASHBOARD
# =========================================================

@app.route("/faculty_dashboard")
def faculty_dashboard():

    if session.get("role") != "faculty":

        return redirect(url_for("login"))

    return render_template(
        "faculty_dashboard.html",
        faculty_name=session.get("faculty_name")
    )


# =========================================================
# FACULTY - MARK ATTENDANCE
# =========================================================

@app.route("/mark_attendance", methods=["GET", "POST"])
def mark_attendance():

    if session.get("role") != "faculty":

        return redirect(url_for("login"))

    db = None
    cursor = None

    try:

        db = get_db()

        if request.method == "POST":

            attendance_date = request.form.get("attendance_date")
            lecture_number = request.form.get("lecture_number")
            subject_name = request.form.get("subject_name")

            faculty_id = session.get("faculty_id")

            present_students = request.form.getlist("status")

            cursor = db.cursor()

            cursor.execute("""
                SELECT student_id
                FROM students
                ORDER BY roll_no
            """)

            all_students = cursor.fetchall()

            for student in all_students:

                student_id = str(student[0])

                if student_id in present_students:

                    status = "Present"

                else:

                    status = "Absent"

                cursor.execute("""
                    INSERT INTO student_attendance
                    (
                        student_id,
                        faculty_id,
                        attendance_date,
                        lecture_number,
                        subject_name,
                        status
                    )
                    VALUES
                    (%s, %s, %s, %s, %s, %s)
                """, (
                    student_id,
                    faculty_id,
                    attendance_date,
                    lecture_number,
                    subject_name,
                    status
                ))

            db.commit()

            cursor.close()
            cursor = None

            return redirect(url_for("faculty_attendance"))


        # =================================================
        # FACULTIES
        # =================================================

        cursor = db.cursor()

        cursor.execute("""
            SELECT
                faculty_id,
                faculty_name
            FROM faculty_registration
            ORDER BY faculty_name
        """)

        faculties = cursor.fetchall()


        # =================================================
        # STUDENTS
        # =================================================

        cursor.execute("""
            SELECT
                student_id,
                roll_no,
                name,
                department,
                year,
                division
            FROM students
            ORDER BY roll_no
        """)

        students = cursor.fetchall()

        return render_template(
            "mark_attendance.html",
            faculties=faculties,
            students=students
        )

    except Exception as e:

        if db:
            db.rollback()

        return f"""
        <h2>Attendance Save Error</h2>
        <p>{e}</p>
        <br>
        <a href="/mark_attendance">Go Back</a>
        """

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# FACULTY - VIEW ATTENDANCE
# =========================================================

@app.route("/faculty_attendance")
def faculty_attendance():

    if session.get("role") != "faculty":

        return redirect(url_for("login"))

    return redirect(url_for("student_attendance"))


# =========================================================
# FACULTY - LIBRARY
# =========================================================

@app.route("/faculty_library")
def faculty_library():

    if session.get("role") != "faculty":

        return redirect(url_for("login"))

    return redirect(url_for("library"))


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin_dashboard")
def admin_dashboard():

    if session.get("role") != "admin":

        return redirect(url_for("login"))

    return render_template(
        "admin_dashboard.html",
        admin_name=session.get("admin_name")
    )


# =========================================================
# ADMIN - VIEW STUDENTS
# =========================================================

@app.route("/admin_students")
def admin_students():

    if session.get("role") != "admin":

        return redirect(url_for("login"))

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                student_id,
                roll_no,
                name,
                department,
                year,
                division,
                username
            FROM students
            ORDER BY roll_no
        """)

        students = cursor.fetchall()

        return render_template(
            "admin_students.html",
            students=students
        )

    except Exception as e:

        return f"""
        <h2>Students Error</h2>
        <p>{e}</p>
        """

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# ADMIN - VIEW FACULTY
# =========================================================

@app.route("/admin_faculty")
def admin_faculty():

    if session.get("role") != "admin":

        return redirect(url_for("login"))

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                faculty_id,
                faculty_name,
                department_name,
                subject_name,
                qualification,
                designation,
                email,
                mobile_number,
                username
            FROM faculty_registration
            ORDER BY faculty_name
        """)

        faculty = cursor.fetchall()

        return render_template(
            "admin_faculty.html",
            faculty=faculty
        )

    except Exception as e:

        return f"""
        <h2>Faculty Error</h2>
        <p>{e}</p>
        """

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# ADMIN + HOD + FACULTY - ADD NOTICE
# =========================================================

@app.route("/add_notice", methods=["GET", "POST"])
def add_notice():

    if session.get("role") not in [
        "admin",
        "hod",
        "faculty"
    ]:

        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form.get("title")
        notice_text = request.form.get("notice_text")

        db = None
        cursor = None

        try:

            db = get_db()
            cursor = db.cursor()

            cursor.execute("""
                INSERT INTO notices
                (
                    title,
                    notice_text
                )
                VALUES
                (%s, %s)
            """, (
                title,
                notice_text
            ))

            db.commit()

            return redirect(url_for("notices"))

        except Exception as e:

            if db:
                db.rollback()

            return f"""
            <h2>Notice Error</h2>
            <p>{e}</p>
            <br>
            <a href="/add_notice">Go Back</a>
            """

        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()

    return render_template("add_notice.html")


# =========================================================
# ADMIN - ADD FEES
# =========================================================

@app.route("/add_fees", methods=["GET", "POST"])
def add_fees():

    if session.get("role") != "admin":

        return redirect(url_for("login"))

    if request.method == "POST":

        student_id = request.form.get("student_id")
        fee_type = request.form.get("fee_type")
        amount = request.form.get("amount")
        due_date = request.form.get("due_date")

        db = None
        cursor = None

        try:

            db = get_db()
            cursor = db.cursor()

            cursor.execute("""
                INSERT INTO fees
                (
                    student_id,
                    fee_type,
                    amount,
                    due_date,
                    status
                )
                VALUES
                (%s, %s, %s, %s, 'Pending')
            """, (
                student_id,
                fee_type,
                amount,
                due_date
            ))

            db.commit()

            return redirect(url_for("admin_dashboard"))

        except Exception as e:

            if db:
                db.rollback()

            return f"""
            <h2>Fee Error</h2>
            <p>{e}</p>
            <br>
            <a href="/add_fees">Go Back</a>
            """

        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()


    # =================================================
    # STUDENTS
    # =================================================

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                student_id,
                roll_no,
                name
            FROM students
            ORDER BY roll_no
        """)

        students = cursor.fetchall()

        return render_template(
            "add_fees.html",
            students=students
        )

    except Exception as e:

        return f"""
        <h2>Students Error</h2>
        <p>{e}</p>
        """

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# HOD DASHBOARD
# =========================================================

@app.route("/hod_dashboard")
def hod_dashboard():

    if session.get("role") != "hod":

        return redirect(url_for("login"))

    return render_template(
        "hod_dashboard.html",
        hod_name=session.get("hod_name"),
        department=session.get("department")
    )


# =========================================================
# HOD - VIEW STUDENTS
# =========================================================

@app.route("/hod_students")
def hod_students():

    if session.get("role") != "hod":

        return redirect(url_for("login"))

    department = session.get("department")

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                roll_no,
                name,
                department,
                year,
                division
            FROM students
            WHERE department = %s
            ORDER BY roll_no
        """, (department,))

        students = cursor.fetchall()

        return render_template(
            "hod_students.html",
            students=students,
            department=department
        )

    except Exception as e:

        return f"""
        <h2>HOD Students Error</h2>
        <p>{e}</p>
        """

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# HOD - VIEW FACULTY
# =========================================================

@app.route("/hod_faculty")
def hod_faculty():

    if session.get("role") != "hod":

        return redirect(url_for("login"))

    department = session.get("department")

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                faculty_name,
                department_name,
                subject_name,
                qualification,
                designation,
                email,
                mobile_number
            FROM faculty_registration
            WHERE department_name = %s
            ORDER BY faculty_name
        """, (department,))

        faculty = cursor.fetchall()

        return render_template(
            "hod_faculty.html",
            faculty=faculty,
            department=department
        )

    except Exception as e:

        return f"""
        <h2>HOD Faculty Error</h2>
        <p>{e}</p>
        """

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# LIBRARIAN DASHBOARD
# =========================================================

@app.route("/librarian_dashboard")
def librarian_dashboard():

    if session.get("role") != "librarian":

        return redirect(url_for("login"))

    return render_template(
        "librarian_dashboard.html",
        librarian_name=session.get("librarian_name")
    )


# =========================================================
# LIBRARY
# STUDENT + FACULTY + LIBRARIAN
# =========================================================

@app.route("/library")
def library():

    role = session.get("role")

    if role not in [
        "student",
        "faculty",
        "librarian"
    ]:

        return redirect(url_for("login"))

    search = request.args.get("search")

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        if search:

            cursor.execute("""
                SELECT
                    book_id,
                    book_name,
                    author,
                    department,
                    quantity
                FROM library_books
                WHERE book_name LIKE %s
                   OR author LIKE %s
                   OR department LIKE %s
                ORDER BY book_name
            """, (
                "%" + search + "%",
                "%" + search + "%",
                "%" + search + "%"
            ))

        else:

            cursor.execute("""
                SELECT
                    book_id,
                    book_name,
                    author,
                    department,
                    quantity
                FROM library_books
                ORDER BY book_name
            """)

        books = cursor.fetchall()

        return render_template(
            "library.html",
            books=books,
            search=search
        )

    except Exception as e:

        return f"""
        <h2>Library Error</h2>
        <p>{e}</p>
        """

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# LIBRARIAN - ADD BOOK
# =========================================================

@app.route("/add_book", methods=["GET", "POST"])
def add_book():

    if session.get("role") != "librarian":

        return redirect(url_for("login"))

    if request.method == "POST":

        book_name = request.form.get("book_name")
        author = request.form.get("author")
        department = request.form.get("department")
        quantity = request.form.get("quantity")

        db = None
        cursor = None

        try:

            db = get_db()
            cursor = db.cursor()

            cursor.execute("""
                INSERT INTO library_books
                (
                    book_name,
                    author,
                    department,
                    quantity
                )
                VALUES
                (%s, %s, %s, %s)
            """, (
                book_name,
                author,
                department,
                quantity
            ))

            db.commit()

            return redirect(url_for("library"))

        except Exception as e:

            if db:
                db.rollback()

            return f"""
            <h2>Add Book Error</h2>
            <p>{e}</p>
            <br>
            <a href="/add_book">Go Back</a>
            """

        finally:

            if cursor:
                cursor.close()

            if db:
                db.close()

    return render_template("add_book.html")


# =========================================================
# LIBRARIAN - DELETE BOOK
# =========================================================

@app.route("/delete_book/<int:book_id>")
def delete_book(book_id):

    if session.get("role") != "librarian":

        return redirect(url_for("login"))

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            DELETE FROM library_books
            WHERE book_id = %s
        """, (book_id,))

        db.commit()

        return redirect(url_for("library"))

    except Exception as e:

        if db:
            db.rollback()

        return f"""
        <h2>Delete Book Error</h2>
        <p>{e}</p>
        <br>
        <a href="/library">Go Back</a>
        """

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# LIBRARIAN - ISSUE BOOK
# =========================================================

@app.route("/issue_book", methods=["GET", "POST"])
def issue_book():

    if session.get("role") != "librarian":

        return redirect(url_for("login"))

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        if request.method == "POST":

            book_id = request.form.get("book_id")
            student_id = request.form.get("student_id")
            issue_date = request.form.get("issue_date")

            # =================================================
            # CHECK BOOK
            # =================================================

            cursor.execute("""
                SELECT quantity
                FROM library_books
                WHERE book_id = %s
            """, (book_id,))

            book = cursor.fetchone()

            if not book:

                return "Book not found."

            if book[0] <= 0:

                return "Book is not available."


            # =================================================
            # CHECK DUPLICATE ISSUE
            # =================================================

            cursor.execute("""
                SELECT issue_id
                FROM library_issues
                WHERE book_id = %s
                AND student_id = %s
                AND status = 'Issued'
            """, (
                book_id,
                student_id
            ))

            existing = cursor.fetchone()

            if existing:

                return "This student already has this book."


            # =================================================
            # RETURN DATE = ISSUE DATE + 10 DAYS
            # =================================================

            try:

                issue_date_obj = datetime.strptime(
                    issue_date,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                return "Invalid issue date."

            return_date = issue_date_obj + timedelta(days=10)


            # =================================================
            # INSERT ISSUE
            # =================================================

            cursor.execute("""
                INSERT INTO library_issues
                (
                    book_id,
                    student_id,
                    issue_date,
                    return_date,
                    status
                )
                VALUES
                (%s, %s, %s, %s, 'Issued')
            """, (
                book_id,
                student_id,
                issue_date_obj,
                return_date
            ))


            # =================================================
            # REDUCE QUANTITY
            # =================================================

            cursor.execute("""
                UPDATE library_books
                SET quantity = quantity - 1
                WHERE book_id = %s
            """, (book_id,))

            db.commit()

            return redirect(url_for("issued_books"))


        # =================================================
        # AVAILABLE BOOKS
        # =================================================

        cursor.execute("""
            SELECT
                book_id,
                book_name,
                author
            FROM library_books
            WHERE quantity > 0
            ORDER BY book_name
        """)

        books = cursor.fetchall()


        # =================================================
        # STUDENTS
        # =================================================

        cursor.execute("""
            SELECT
                student_id,
                roll_no,
                name
            FROM students
            ORDER BY roll_no
        """)

        students = cursor.fetchall()

        return render_template(
            "issue_book.html",
            books=books,
            students=students
        )

    except Exception as e:

        if db:
            db.rollback()

        return f"""
        <h2>Issue Book Error</h2>
        <p>{e}</p>
        <br>
        <a href="/issue_book">Go Back</a>
        """

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# LIBRARIAN - ISSUED BOOKS
# =========================================================

@app.route("/issued_books")
def issued_books():

    if session.get("role") != "librarian":

        return redirect(url_for("login"))

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT
                li.issue_id,
                s.roll_no,
                s.name,
                lb.book_name,
                li.issue_date,
                li.return_date,
                li.actual_return_date,
                li.status
            FROM library_issues li
            INNER JOIN students s
                ON li.student_id = s.student_id
            INNER JOIN library_books lb
                ON li.book_id = lb.book_id
            ORDER BY li.issue_date DESC
        """)

        issues = cursor.fetchall()

        return render_template(
            "issued_books.html",
            issues=issues
        )

    except Exception as e:

        return f"""
        <h2>Issued Books Error</h2>
        <p>{e}</p>
        """

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# LIBRARIAN - RETURN BOOK
# =========================================================

@app.route("/return_book/<int:issue_id>")
def return_book(issue_id):

    if session.get("role") != "librarian":

        return redirect(url_for("login"))

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        # =================================================
        # FIND BOOK
        # =================================================

        cursor.execute("""
            SELECT book_id
            FROM library_issues
            WHERE issue_id = %s
            AND status = 'Issued'
        """, (issue_id,))

        issue = cursor.fetchone()

        if not issue:

            return "Book already returned or issue not found."

        book_id = issue[0]


        # =================================================
        # UPDATE ISSUE
        # =================================================

        cursor.execute("""
            UPDATE library_issues
            SET
                actual_return_date = CURRENT_DATE,
                status = 'Returned'
            WHERE issue_id = %s
        """, (issue_id,))


        # =================================================
        # INCREASE QUANTITY
        # =================================================

        cursor.execute("""
            UPDATE library_books
            SET quantity = quantity + 1
            WHERE book_id = %s
        """, (book_id,))

        db.commit()

        return redirect(url_for("issued_books"))

    except Exception as e:

        if db:
            db.rollback()

        return f"""
        <h2>Return Book Error</h2>
        <p>{e}</p>
        <br>
        <a href="/issued_books">Go Back</a>
        """

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT 1")

        result = cursor.fetchone()

        if result and result[0] == 1:

            return "Database connection successful!"

        return "Database connection failed."

    except Exception as e:

        return f"Database connection error: {e}", 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )

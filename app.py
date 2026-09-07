import os
from datetime import datetime, timedelta

import mysql.connector
from mysql.connector import Error

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
)


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "college-management-secret-key-2026"
)


# =========================================================
# DATABASE CONFIGURATION
# =========================================================
#
# TiDB Cloud
#
# HOST:
# gateway01.ap-southeast-1.prod.aws.tidbcloud.com
#
# PORT:
# 4000
#
# DATABASE:
# defaultdb
#
# USER:
# 3iLkfSZQtMHh9So.root
#
# PASSWORD:
# Render Environment Variable se aayega.
#
# =========================================================

TIDB_HOST = os.environ.get(
    "TIDB_HOST",
    "gateway01.ap-southeast-1.prod.aws.tidbcloud.com"
)

TIDB_PORT = int(
    os.environ.get(
        "TIDB_PORT",
        "4000"
    )
)

TIDB_USER = os.environ.get(
    "TIDB_USER",
    "3iLkfSZQtMHh9So.root"
)

TIDB_PASSWORD = os.environ.get(
    "TIDB_PASSWORD",
    ""
)

TIDB_DATABASE = os.environ.get(
    "TIDB_DATABASE",
    "defaultdb"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():

    if not TIDB_PASSWORD:
        raise RuntimeError(
            "TIDB_PASSWORD is missing. "
            "Please add your TiDB Cloud password "
            "in Render Environment Variables."
        )

    if not TIDB_HOST:
        raise RuntimeError(
            "TIDB_HOST is missing."
        )

    if TIDB_HOST.lower() in (
        "localhost",
        "127.0.0.1",
        "::1"
    ):
        raise RuntimeError(
            "Invalid database host. "
            "Do not use localhost on Render."
        )

    try:

        connection = mysql.connector.connect(
            host=TIDB_HOST,
            port=TIDB_PORT,
            user=TIDB_USER,
            password=TIDB_PASSWORD,
            database=TIDB_DATABASE,

            # TiDB Cloud requires secure connection.
            ssl_disabled=False,

            connection_timeout=20,
            autocommit=False,
        )

        if not connection.is_connected():
            raise RuntimeError(
                "Could not connect to TiDB Cloud."
            )

        return connection

    except Error as e:

        raise RuntimeError(
            f"TiDB Cloud connection failed: {e}"
        )


# =========================================================
# DATABASE ERROR PAGE
# =========================================================

def db_error_page(
    title,
    error,
    back_url="/login"
):

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>{title}</title>

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1"
        >

        <style>

            body {{
                margin: 0;
                padding: 40px;
                font-family: Arial, sans-serif;
                background: #f4f7fb;
            }}

            .box {{
                max-width: 700px;
                margin: 60px auto;
                padding: 30px;
                background: white;
                border-radius: 14px;
                box-shadow:
                    0 5px 25px
                    rgba(0,0,0,.10);
            }}

            h2 {{
                color: #d93025;
            }}

            .error {{
                background: #fff3f3;
                padding: 15px;
                border-radius: 8px;
                color: #444;
                word-break: break-word;
            }}

            a {{
                display: inline-block;
                margin-top: 20px;
                padding: 11px 20px;
                background: #1677ff;
                color: white;
                text-decoration: none;
                border-radius: 7px;
            }}

        </style>

    </head>

    <body>

        <div class="box">

            <h2>{title}</h2>

            <div class="error">
                {error}
            </div>

            <a href="{back_url}">
                Go Back
            </a>

        </div>

    </body>

    </html>
    """


# =========================================================
# NO CACHE
# =========================================================

@app.after_request
def add_no_cache(response):

    response.headers[
        "Cache-Control"
    ] = "no-store, no-cache, must-revalidate, max-age=0"

    response.headers[
        "Pragma"
    ] = "no-cache"

    response.headers[
        "Expires"
    ] = "0"

    return response


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "home.html"
    )


# =========================================================
# SIGN IN / REGISTRATION
# =========================================================

@app.route(
    "/signin",
    methods=["GET", "POST"]
)
def signin():

    if request.method == "GET":

        return render_template(
            "signin.html"
        )

    role = (
        request.form.get("role")
        or ""
    ).strip().lower()

    username = (
        request.form.get("username")
        or ""
    ).strip()

    password = (
        request.form.get("password")
        or ""
    ).strip()

    if not username or not password:

        return db_error_page(
            "Registration Error",
            "Username and password are required.",
            "/signin"
        )

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        # =================================================
        # STUDENT
        # =================================================

        if role == "student":

            roll_no = (
                request.form.get("roll_no")
                or ""
            ).strip()

            name = (
                request.form.get("name")
                or ""
            ).strip()

            department = (
                request.form.get("department")
                or ""
            ).strip()

            year = (
                request.form.get("year")
                or ""
            ).strip()

            division = (
                request.form.get("division")
                or ""
            ).strip()

            if not roll_no:

                return db_error_page(
                    "Student Registration Error",
                    "Please enter Roll Number.",
                    "/signin"
                )

            cursor.execute(
                """
                SELECT student_id
                FROM students
                WHERE roll_no = %s
                """,
                (roll_no,)
            )

            if cursor.fetchone():

                return db_error_page(
                    "Student Registration Error",
                    "Roll Number already exists.",
                    "/signin"
                )

            cursor.execute(
                """
                SELECT student_id
                FROM students
                WHERE username = %s
                """,
                (username,)
            )

            if cursor.fetchone():

                return db_error_page(
                    "Student Registration Error",
                    "Username already exists.",
                    "/signin"
                )

            cursor.execute(
                """
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
                """,
                (
                    roll_no,
                    name,
                    department,
                    year,
                    division,
                    username,
                    password
                )
            )

            db.commit()

            return redirect(
                url_for("login")
            )

        # =================================================
        # FACULTY
        # =================================================

        if role == "faculty":

            faculty_name = (
                request.form.get(
                    "faculty_name"
                )
                or ""
            ).strip()

            department_name = (
                request.form.get(
                    "department_name"
                )
                or ""
            ).strip()

            subject_name = (
                request.form.get(
                    "subject_name"
                )
                or ""
            ).strip()

            qualification = (
                request.form.get(
                    "qualification"
                )
                or ""
            ).strip()

            designation = (
                request.form.get(
                    "designation"
                )
                or ""
            ).strip()

            email = (
                request.form.get(
                    "email"
                )
                or ""
            ).strip()

            mobile_number = (
                request.form.get(
                    "mobile_number"
                )
                or ""
            ).strip()

            cursor.execute(
                """
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
                (%s, %s, %s, %s, %s,
                 %s, %s, %s, %s)
                """,
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
            )

            db.commit()

            return redirect(
                url_for("login")
            )

        # =================================================
        # ADMIN
        # =================================================

        if role == "admin":

            admin_name = (
                request.form.get(
                    "admin_name"
                )
                or ""
            ).strip()

            email = (
                request.form.get(
                    "admin_email"
                )
                or ""
            ).strip()

            cursor.execute(
                """
                INSERT INTO administrator
                (
                    admin_name,
                    email,
                    username,
                    password
                )
                VALUES
                (%s, %s, %s, %s)
                """,
                (
                    admin_name,
                    email,
                    username,
                    password
                )
            )

            db.commit()

            return redirect(
                url_for("login")
            )

        # =================================================
        # HOD
        # =================================================

        if role == "hod":

            hod_name = (
                request.form.get(
                    "hod_name"
                )
                or ""
            ).strip()

            department_name = (
                request.form.get(
                    "hod_department"
                )
                or ""
            ).strip()

            email = (
                request.form.get(
                    "hod_email"
                )
                or ""
            ).strip()

            mobile_number = (
                request.form.get(
                    "hod_mobile"
                )
                or ""
            ).strip()

            cursor.execute(
                """
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
                """,
                (
                    hod_name,
                    department_name,
                    email,
                    mobile_number,
                    username,
                    password
                )
            )

            db.commit()

            return redirect(
                url_for("login")
            )

        # =================================================
        # LIBRARIAN
        # =================================================

        if role == "librarian":

            librarian_name = (
                request.form.get(
                    "librarian_name"
                )
                or ""
            ).strip()

            email = (
                request.form.get(
                    "librarian_email"
                )
                or ""
            ).strip()

            mobile_number = (
                request.form.get(
                    "librarian_mobile"
                )
                or ""
            ).strip()

            cursor.execute(
                """
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
                """,
                (
                    librarian_name,
                    email,
                    mobile_number,
                    username,
                    password
                )
            )

            db.commit()

            return redirect(
                url_for("login")
            )

        return db_error_page(
            "Registration Error",
            "Invalid role selected.",
            "/signin"
        )

    except Error as e:

        if db:
            db.rollback()

        return db_error_page(
            "Registration Database Error",
            e,
            "/signin"
        )

    except Exception as e:

        if db:
            db.rollback()

        return db_error_page(
            "Registration Error",
            e,
            "/signin"
        )

    finally:

        if cursor:

            try:
                cursor.close()
            except Exception:
                pass

        if db:

            try:
                db.close()
            except Exception:
                pass


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "GET":

        return render_template(
            "login.html"
        )

    role = (
        request.form.get("role")
        or ""
    ).strip().lower()

    username = (
        request.form.get("username")
        or ""
    ).strip()

    password = (
        request.form.get("password")
        or ""
    ).strip()

    if not username or not password:

        return db_error_page(
            "Login Error",
            "Username and password are required.",
            "/login"
        )

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        # =================================================
        # STUDENT
        # =================================================

        if role == "student":

            cursor.execute(
                """
                SELECT
                    student_id,
                    name,
                    department,
                    year,
                    division
                FROM students
                WHERE username = %s
                  AND password = %s
                """,
                (
                    username,
                    password
                )
            )

            user = cursor.fetchone()

            if user:

                session.clear()

                session["role"] = "student"
                session["student_id"] = user[0]
                session["student_name"] = user[1]
                session["department"] = user[2]
                session["year"] = user[3]
                session["division"] = user[4]

                return redirect(
                    url_for("dashboard")
                )

            return db_error_page(
                "Login Failed",
                "Invalid Student Username or Password.",
                "/login"
            )

        # =================================================
        # FACULTY
        # =================================================

        if role == "faculty":

            cursor.execute(
                """
                SELECT
                    faculty_id,
                    faculty_name,
                    department_name,
                    subject_name
                FROM faculty_registration
                WHERE username = %s
                  AND password = %s
                """,
                (
                    username,
                    password
                )
            )

            user = cursor.fetchone()

            if user:

                session.clear()

                session["role"] = "faculty"
                session["faculty_id"] = user[0]
                session["faculty_name"] = user[1]
                session["department"] = user[2]
                session["subject"] = user[3]

                return redirect(
                    url_for("faculty_dashboard")
                )

            return db_error_page(
                "Login Failed",
                "Invalid Faculty Username or Password.",
                "/login"
            )

        # =================================================
        # ADMIN
        # =================================================

        if role == "admin":

            cursor.execute(
                """
                SELECT
                    admin_id,
                    admin_name
                FROM administrator
                WHERE username = %s
                  AND password = %s
                """,
                (
                    username,
                    password
                )
            )

            user = cursor.fetchone()

            if user:

                session.clear()

                session["role"] = "admin"
                session["admin_id"] = user[0]
                session["admin_name"] = user[1]

                return redirect(
                    url_for("admin_dashboard")
                )

            return db_error_page(
                "Login Failed",
                "Invalid Administrator Username or Password.",
                "/login"
            )

        # =================================================
        # HOD
        # =================================================

        if role == "hod":

            cursor.execute(
                """
                SELECT
                    hod_id,
                    hod_name,
                    department_name
                FROM department_hod
                WHERE username = %s
                  AND password = %s
                """,
                (
                    username,
                    password
                )
            )

            user = cursor.fetchone()

            if user:

                session.clear()

                session["role"] = "hod"
                session["hod_id"] = user[0]
                session["hod_name"] = user[1]
                session["department"] = user[2]

                return redirect(
                    url_for("hod_dashboard")
                )

            return db_error_page(
                "Login Failed",
                "Invalid HOD Username or Password.",
                "/login"
            )

        # =================================================
        # LIBRARIAN
        # =================================================

        if role == "librarian":

            cursor.execute(
                """
                SELECT
                    librarian_id,
                    librarian_name
                FROM librarian
                WHERE username = %s
                  AND password = %s
                """,
                (
                    username,
                    password
                )
            )

            user = cursor.fetchone()

            if user:

                session.clear()

                session["role"] = "librarian"
                session["librarian_id"] = user[0]
                session["librarian_name"] = user[1]

                return redirect(
                    url_for("librarian_dashboard")
                )

            return db_error_page(
                "Login Failed",
                "Invalid Librarian Username or Password.",
                "/login"
            )

        return db_error_page(
            "Login Error",
            "Invalid role.",
            "/login"
        )

    except Exception as e:

        return db_error_page(
            "Database Error",
            e,
            "/login"
        )

    finally:

        if cursor:

            try:
                cursor.close()
            except Exception:
                pass

        if db:

            try:
                db.close()
            except Exception:
                pass


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# STUDENT DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if session.get("role") != "student":

        return redirect(
            url_for("login")
        )

    return render_template(
        "dashboard.html",
        student_name=session.get(
            "student_name"
        )
    )


# =========================================================
# STUDENT ATTENDANCE
# =========================================================

@app.route("/student_attendance")
def student_attendance():

    role = session.get("role")

    if role not in (
        "student",
        "faculty",
        "admin",
        "hod"
    ):

        return redirect(
            url_for("login")
        )

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        query = """
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
        """

        if role == "student":

            query += """
                WHERE sa.student_id = %s
                ORDER BY
                    sa.attendance_date DESC,
                    sa.lecture_number DESC
            """

            cursor.execute(
                query,
                (
                    session.get("student_id"),
                )
            )

        elif role == "faculty":

            query += """
                WHERE sa.faculty_id = %s
                ORDER BY
                    sa.attendance_date DESC,
                    sa.lecture_number DESC
            """

            cursor.execute(
                query,
                (
                    session.get("faculty_id"),
                )
            )

        elif role == "hod":

            query += """
                WHERE s.department = %s
                ORDER BY
                    sa.attendance_date DESC,
                    sa.lecture_number DESC
            """

            cursor.execute(
                query,
                (
                    session.get("department"),
                )
            )

        else:

            query += """
                ORDER BY
                    sa.attendance_date DESC,
                    sa.lecture_number DESC
            """

            cursor.execute(query)

        attendance_data = cursor.fetchall()

        return render_template(
            "student_attendance.html",
            attendance_data=attendance_data,
            user_role=role
        )

    except Exception as e:

        return db_error_page(
            "Attendance Error",
            e,
            "/dashboard"
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# MY ATTENDANCE
# =========================================================

@app.route("/my_attendance")
def my_attendance():

    if session.get("role") != "student":

        return redirect(
            url_for("login")
        )

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
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
            """,
            (
                session.get("student_id"),
            )
        )

        attendance = cursor.fetchall()

        return render_template(
            "my_attendance.html",
            attendance=attendance
        )

    except Exception as e:

        return db_error_page(
            "My Attendance Error",
            e,
            "/dashboard"
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# MY BOOKS
# =========================================================

@app.route("/my_books")
def my_books():

    if session.get("role") != "student":

        return redirect(
            url_for("login")
        )

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
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
            """,
            (
                session.get("student_id"),
            )
        )

        books = cursor.fetchall()

        return render_template(
            "my_books.html",
            books=books
        )

    except Exception as e:

        return db_error_page(
            "My Books Error",
            e,
            "/dashboard"
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# STUDENT FEES
# =========================================================

@app.route("/fees")
def fees():

    if session.get("role") != "student":

        return redirect(
            url_for("login")
        )

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT
                fee_type,
                amount,
                due_date,
                status
            FROM fees
            WHERE student_id = %s
            ORDER BY due_date
            """,
            (
                session.get("student_id"),
            )
        )

        fee_data = cursor.fetchall()

        return render_template(
            "fees.html",
            fee_data=fee_data
        )

    except Exception as e:

        return db_error_page(
            "Fees Error",
            e,
            "/dashboard"
        )

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

    if role not in (
        "student",
        "faculty",
        "admin",
        "hod"
    ):

        return redirect(
            url_for("login")
        )

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT
                notice_id,
                title,
                notice_text,
                created_at
            FROM notices
            ORDER BY created_at DESC
            """
        )

        notice_data = cursor.fetchall()

        return render_template(
            "notices.html",
            notice_data=notice_data,
            user_role=role
        )

    except Exception as e:

        return db_error_page(
            "Notice Error",
            e,
            "/dashboard"
        )

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

        return redirect(
            url_for("login")
        )

    return render_template(
        "faculty_dashboard.html",
        faculty_name=session.get(
            "faculty_name"
        )
    )


# =========================================================
# MARK ATTENDANCE
# =========================================================

@app.route(
    "/mark_attendance",
    methods=["GET", "POST"]
)
def mark_attendance():

    if session.get("role") != "faculty":

        return redirect(
            url_for("login")
        )

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        if request.method == "POST":

            attendance_date = (
                request.form.get(
                    "attendance_date"
                )
                or ""
            ).strip()

            lecture_number = (
                request.form.get(
                    "lecture_number"
                )
                or ""
            ).strip()

            subject_name = (
                request.form.get(
                    "subject_name"
                )
                or session.get(
                    "subject"
                )
                or ""
            ).strip()

            present_students = set(
                request.form.getlist(
                    "status"
                )
            )

            if not attendance_date:

                return db_error_page(
                    "Attendance Error",
                    "Attendance date is required.",
                    "/mark_attendance"
                )

            cursor.execute(
                """
                SELECT
                    student_id
                FROM students
                ORDER BY roll_no
                """
            )

            students = cursor.fetchall()

            for row in students:

                student_id = str(
                    row[0]
                )

                status = (
                    "Present"
                    if student_id in present_students
                    else "Absent"
                )

                cursor.execute(
                    """
                    SELECT attendance_id
                    FROM student_attendance
                    WHERE student_id = %s
                      AND faculty_id = %s
                      AND attendance_date = %s
                      AND lecture_number = %s
                      AND subject_name = %s
                    LIMIT 1
                    """,
                    (
                        row[0],
                        session.get("faculty_id"),
                        attendance_date,
                        lecture_number,
                        subject_name
                    )
                )

                existing = cursor.fetchone()

                if existing:

                    cursor.execute(
                        """
                        UPDATE student_attendance
                        SET status = %s
                        WHERE attendance_id = %s
                        """,
                        (
                            status,
                            existing[0]
                        )
                    )

                else:

                    cursor.execute(
                        """
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
                        """,
                        (
                            row[0],
                            session.get("faculty_id"),
                            attendance_date,
                            lecture_number,
                            subject_name,
                            status
                        )
                    )

            db.commit()

            return redirect(
                url_for(
                    "faculty_attendance"
                )
            )

        cursor.execute(
            """
            SELECT
                student_id,
                roll_no,
                name,
                department,
                year,
                division
            FROM students
            ORDER BY roll_no
            """
        )

        students = cursor.fetchall()

        return render_template(
            "mark_attendance.html",
            students=students,
            faculties=[],
            faculty_name=session.get(
                "faculty_name"
            )
        )

    except Exception as e:

        if db:

            try:
                db.rollback()
            except Exception:
                pass

        return db_error_page(
            "Attendance Save Error",
            e,
            "/mark_attendance"
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# FACULTY ATTENDANCE
# =========================================================

@app.route("/faculty_attendance")
def faculty_attendance():

    if session.get("role") != "faculty":

        return redirect(
            url_for("login")
        )

    return redirect(
        url_for("student_attendance")
    )


# =========================================================
# FACULTY LIBRARY
# =========================================================

@app.route("/faculty_library")
def faculty_library():

    if session.get("role") != "faculty":

        return redirect(
            url_for("login")
        )

    return redirect(
        url_for("library")
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin_dashboard")
def admin_dashboard():

    if session.get("role") != "admin":

        return redirect(
            url_for("login")
        )

    return render_template(
        "admin_dashboard.html",
        admin_name=session.get(
            "admin_name"
        )
    )


# =========================================================
# ADMIN STUDENTS
# =========================================================

@app.route("/admin_students")
def admin_students():

    if session.get("role") != "admin":

        return redirect(
            url_for("login")
        )

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
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
            """
        )

        students = cursor.fetchall()

        return render_template(
            "admin_students.html",
            students=students
        )

    except Exception as e:

        return db_error_page(
            "Students Error",
            e,
            "/admin_dashboard"
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# ADMIN FACULTY
# =========================================================

@app.route("/admin_faculty")
def admin_faculty():

    if session.get("role") != "admin":

        return redirect(
            url_for("login")
        )

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
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
            """
        )

        faculty = cursor.fetchall()

        return render_template(
            "admin_faculty.html",
            faculty=faculty
        )

    except Exception as e:

        return db_error_page(
            "Faculty Error",
            e,
            "/admin_dashboard"
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# ADD NOTICE
# =========================================================

@app.route(
    "/add_notice",
    methods=["GET", "POST"]
)
def add_notice():

    if session.get("role") not in (
        "admin",
        "hod",
        "faculty"
    ):

        return redirect(
            url_for("login")
        )

    if request.method == "GET":

        return render_template(
            "add_notice.html"
        )

    title = (
        request.form.get("title")
        or ""
    ).strip()

    notice_text = (
        request.form.get("notice_text")
        or ""
    ).strip()

    if not title or not notice_text:

        return db_error_page(
            "Notice Error",
            "Title and notice text are required.",
            "/add_notice"
        )

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO notices
            (
                title,
                notice_text
            )
            VALUES
            (%s, %s)
            """,
            (
                title,
                notice_text
            )
        )

        db.commit()

        return redirect(
            url_for("notices")
        )

    except Exception as e:

        if db:
            db.rollback()

        return db_error_page(
            "Notice Error",
            e,
            "/add_notice"
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# ADD FEES
# =========================================================

@app.route(
    "/add_fees",
    methods=["GET", "POST"]
)
def add_fees():

    if session.get("role") != "admin":

        return redirect(
            url_for("login")
        )

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        if request.method == "POST":

            student_id = (
                request.form.get(
                    "student_id"
                )
                or ""
            ).strip()

            fee_type = (
                request.form.get(
                    "fee_type"
                )
                or ""
            ).strip()

            amount = (
                request.form.get(
                    "amount"
                )
                or ""
            ).strip()

            due_date = (
                request.form.get(
                    "due_date"
                )
                or ""
            ).strip()

            if not student_id:

                return db_error_page(
                    "Fee Error",
                    "Please select a student.",
                    "/add_fees"
                )

            if not fee_type:

                return db_error_page(
                    "Fee Error",
                    "Please select a fee type.",
                    "/add_fees"
                )

            if not amount:

                return db_error_page(
                    "Fee Error",
                    "Please enter amount.",
                    "/add_fees"
                )

            if not due_date:

                return db_error_page(
                    "Fee Error",
                    "Please select due date.",
                    "/add_fees"
                )

            try:

                amount_value = float(amount)

                if amount_value < 0:

                    raise ValueError

            except ValueError:

                return db_error_page(
                    "Fee Error",
                    "Invalid fee amount.",
                    "/add_fees"
                )

            cursor.execute(
                """
                SELECT student_id
                FROM students
                WHERE student_id = %s
                """,
                (
                    student_id,
                )
            )

            if not cursor.fetchone():

                return db_error_page(
                    "Fee Error",
                    "Selected student does not exist.",
                    "/add_fees"
                )

            cursor.execute(
                """
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
                """,
                (
                    student_id,
                    fee_type,
                    amount_value,
                    due_date
                )
            )

            db.commit()

            return redirect(
                url_for("admin_fees")
            )

        cursor.execute(
            """
            SELECT
                student_id,
                roll_no,
                name,
                department,
                year,
                division
            FROM students
            ORDER BY roll_no
            """
        )

        students = cursor.fetchall()

        return render_template(
            "add_fees.html",
            students=students
        )

    except Exception as e:

        if db:
            db.rollback()

        return db_error_page(
            "Fee Error",
            e,
            "/add_fees"
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# ADMIN FEES
# =========================================================

@app.route("/admin_fees")
def admin_fees():

    if session.get("role") != "admin":

        return redirect(
            url_for("login")
        )

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT
                f.fee_id,
                s.student_id,
                s.roll_no,
                s.name,
                f.fee_type,
                f.amount,
                f.due_date,
                f.status
            FROM fees f
            INNER JOIN students s
                ON f.student_id = s.student_id
            ORDER BY f.fee_id DESC
            """
        )

        fees_data = cursor.fetchall()

        return render_template(
            "admin_fees.html",
            fees_data=fees_data
        )

    except Exception as e:

        return db_error_page(
            "Admin Fees Error",
            e,
            "/admin_dashboard"
        )

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

        return redirect(
            url_for("login")
        )

    return render_template(
        "hod_dashboard.html",
        hod_name=session.get(
            "hod_name"
        ),
        department=session.get(
            "department"
        )
    )


# =========================================================
# HOD STUDENTS
# =========================================================

@app.route("/hod_students")
def hod_students():

    if session.get("role") != "hod":

        return redirect(
            url_for("login")
        )

    department = session.get(
        "department"
    )

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT
                roll_no,
                name,
                department,
                year,
                division
            FROM students
            WHERE department = %s
            ORDER BY roll_no
            """,
            (
                department,
            )
        )

        students = cursor.fetchall()

        return render_template(
            "hod_students.html",
            students=students,
            department=department
        )

    except Exception as e:

        return db_error_page(
            "HOD Students Error",
            e,
            "/hod_dashboard"
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# HOD FACULTY
# =========================================================

@app.route("/hod_faculty")
def hod_faculty():

    if session.get("role") != "hod":

        return redirect(
            url_for("login")
        )

    department = session.get(
        "department"
    )

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
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
            """,
            (
                department,
            )
        )

        faculty = cursor.fetchall()

        return render_template(
            "hod_faculty.html",
            faculty=faculty,
            department=department
        )

    except Exception as e:

        return db_error_page(
            "HOD Faculty Error",
            e,
            "/hod_dashboard"
        )

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

        return redirect(
            url_for("login")
        )

    return render_template(
        "librarian_dashboard.html",
        librarian_name=session.get(
            "librarian_name"
        )
    )


# =========================================================
# LIBRARY
# =========================================================

@app.route("/library")
def library():

    role = session.get("role")

    if role not in (
        "student",
        "faculty",
        "librarian"
    ):

        return redirect(
            url_for("login")
        )

    search = (
        request.args.get("search")
        or ""
    ).strip()

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        if search:

            keyword = f"%{search}%"

            cursor.execute(
                """
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
                """,
                (
                    keyword,
                    keyword,
                    keyword
                )
            )

        else:

            cursor.execute(
                """
                SELECT
                    book_id,
                    book_name,
                    author,
                    department,
                    quantity
                FROM library_books
                ORDER BY book_name
                """
            )

        books = cursor.fetchall()

        return render_template(
            "library.html",
            books=books,
            search=search
        )

    except Exception as e:

        return db_error_page(
            "Library Error",
            e,
            "/dashboard"
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# ADD BOOK
# =========================================================

@app.route(
    "/add_book",
    methods=["GET", "POST"]
)
def add_book():

    if session.get("role") != "librarian":

        return redirect(
            url_for("login")
        )

    if request.method == "GET":

        return render_template(
            "add_book.html"
        )

    book_name = (
        request.form.get("book_name")
        or ""
    ).strip()

    author = (
        request.form.get("author")
        or ""
    ).strip()

    department = (
        request.form.get("department")
        or ""
    ).strip()

    quantity = (
        request.form.get("quantity")
        or "0"
    ).strip()

    try:

        quantity_value = int(quantity)

        if quantity_value < 0:
            raise ValueError

    except ValueError:

        return db_error_page(
            "Add Book Error",
            "Quantity must be a valid positive number.",
            "/add_book"
        )

    if not book_name:

        return db_error_page(
            "Add Book Error",
            "Book name is required.",
            "/add_book"
        )

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO library_books
            (
                book_name,
                author,
                department,
                quantity
            )
            VALUES
            (%s, %s, %s, %s)
            """,
            (
                book_name,
                author,
                department,
                quantity_value
            )
        )

        db.commit()

        return redirect(
            url_for("library")
        )

    except Exception as e:

        if db:
            db.rollback()

        return db_error_page(
            "Add Book Error",
            e,
            "/add_book"
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# DELETE BOOK
# =========================================================

@app.route(
    "/delete_book/<int:book_id>"
)
def delete_book(book_id):

    if session.get("role") != "librarian":

        return redirect(
            url_for("login")
        )

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT issue_id
            FROM library_issues
            WHERE book_id = %s
              AND status = 'Issued'
            LIMIT 1
            """,
            (
                book_id,
            )
        )

        if cursor.fetchone():

            return db_error_page(
                "Delete Book Error",
                "This book is currently issued and cannot be deleted.",
                "/library"
            )

        cursor.execute(
            """
            DELETE FROM library_books
            WHERE book_id = %s
            """,
            (
                book_id,
            )
        )

        db.commit()

        return redirect(
            url_for("library")
        )

    except Exception as e:

        if db:
            db.rollback()

        return db_error_page(
            "Delete Book Error",
            e,
            "/library"
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# ISSUE BOOK
# =========================================================

@app.route(
    "/issue_book",
    methods=["GET", "POST"]
)
def issue_book():

    if session.get("role") != "librarian":

        return redirect(
            url_for("login")
        )

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        if request.method == "POST":

            book_id = (
                request.form.get(
                    "book_id"
                )
                or ""
            ).strip()

            student_id = (
                request.form.get(
                    "student_id"
                )
                or ""
            ).strip()

            issue_date = (
                request.form.get(
                    "issue_date"
                )
                or ""
            ).strip()

            if not book_id or not student_id:

                return db_error_page(
                    "Issue Book Error",
                    "Book and student are required.",
                    "/issue_book"
                )

            cursor.execute(
                """
                SELECT quantity
                FROM library_books
                WHERE book_id = %s
                FOR UPDATE
                """,
                (
                    book_id,
                )
            )

            book = cursor.fetchone()

            if not book:

                return db_error_page(
                    "Issue Book Error",
                    "Book not found.",
                    "/issue_book"
                )

            if int(book[0]) <= 0:

                return db_error_page(
                    "Issue Book Error",
                    "Book is not available.",
                    "/issue_book"
                )

            cursor.execute(
                """
                SELECT student_id
                FROM students
                WHERE student_id = %s
                """,
                (
                    student_id,
                )
            )

            if not cursor.fetchone():

                return db_error_page(
                    "Issue Book Error",
                    "Student not found.",
                    "/issue_book"
                )

            cursor.execute(
                """
                SELECT issue_id
                FROM library_issues
                WHERE book_id = %s
                  AND student_id = %s
                  AND status = 'Issued'
                LIMIT 1
                """,
                (
                    book_id,
                    student_id
                )
            )

            if cursor.fetchone():

                return db_error_page(
                    "Issue Book Error",
                    "This student already has this book.",
                    "/issue_book"
                )

            try:

                issue_date_obj = datetime.strptime(
                    issue_date,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                return db_error_page(
                    "Issue Book Error",
                    "Invalid issue date.",
                    "/issue_book"
                )

            return_date = (
                issue_date_obj
                + timedelta(days=10)
            )

            cursor.execute(
                """
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
                """,
                (
                    book_id,
                    student_id,
                    issue_date_obj,
                    return_date
                )
            )

            cursor.execute(
                """
                UPDATE library_books
                SET quantity = quantity - 1
                WHERE book_id = %s
                  AND quantity > 0
                """,
                (
                    book_id,
                )
            )

            if cursor.rowcount != 1:

                db.rollback()

                return db_error_page(
                    "Issue Book Error",
                    "Book quantity could not be updated.",
                    "/issue_book"
                )

            db.commit()

            return redirect(
                url_for("issued_books")
            )

        cursor.execute(
            """
            SELECT
                book_id,
                book_name,
                author
            FROM library_books
            WHERE quantity > 0
            ORDER BY book_name
            """
        )

        books = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                student_id,
                roll_no,
                name
            FROM students
            ORDER BY roll_no
            """
        )

        students = cursor.fetchall()

        return render_template(
            "issue_book.html",
            books=books,
            students=students
        )

    except Exception as e:

        if db:
            db.rollback()

        return db_error_page(
            "Issue Book Error",
            e,
            "/issue_book"
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# ISSUED BOOKS
# =========================================================

@app.route("/issued_books")
def issued_books():

    if session.get("role") != "librarian":

        return redirect(
            url_for("login")
        )

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
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
            """
        )

        issues = cursor.fetchall()

        return render_template(
            "issued_books.html",
            issues=issues
        )

    except Exception as e:

        return db_error_page(
            "Issued Books Error",
            e,
            "/librarian_dashboard"
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# RETURN BOOK
# =========================================================

@app.route(
    "/return_book/<int:issue_id>"
)
def return_book(issue_id):

    if session.get("role") != "librarian":

        return redirect(
            url_for("login")
        )

    db = None
    cursor = None

    try:

        db = get_db()
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT
                book_id
            FROM library_issues
            WHERE issue_id = %s
              AND status = 'Issued'
            FOR UPDATE
            """,
            (
                issue_id,
            )
        )

        issue = cursor.fetchone()

        if not issue:

            return db_error_page(
                "Return Book Error",
                "Book already returned or issue not found.",
                "/issued_books"
            )

        book_id = issue[0]

        cursor.execute(
            """
            UPDATE library_issues
            SET
                actual_return_date = CURRENT_DATE,
                status = 'Returned'
            WHERE issue_id = %s
              AND status = 'Issued'
            """,
            (
                issue_id,
            )
        )

        if cursor.rowcount != 1:

            db.rollback()

            return db_error_page(
                "Return Book Error",
                "Book could not be returned.",
                "/issued_books"
            )

        cursor.execute(
            """
            UPDATE library_books
            SET quantity = quantity + 1
            WHERE book_id = %s
            """,
            (
                book_id,
            )
        )

        db.commit()

        return redirect(
            url_for("issued_books")
        )

    except Exception as e:

        if db:
            db.rollback()

        return db_error_page(
            "Return Book Error",
            e,
            "/issued_books"
        )

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

        cursor.execute(
            "SELECT DATABASE(), 1"
        )

        result = cursor.fetchone()

        database_name = result[0]

        return (
            f"OK - TiDB Cloud connected. "
            f"Database: {database_name}"
        )

    except Exception as e:

        return (
            f"Database connection error: {e}"
        ), 500

    finally:

        if cursor:

            try:
                cursor.close()
            except Exception:
                pass

        if db:

            try:
                db.close()
            except Exception:
                pass


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            "10000"
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
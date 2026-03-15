from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "ndc_bca_hackathon_secret_key_change_me_2026"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

DB_PATH = os.path.join(os.path.dirname(__file__), "database3.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        # Users
        db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            team_name TEXT UNIQUE,
            is_admin INTEGER DEFAULT 0
        )
        """)

        # Scores
        db.execute("""
        CREATE TABLE IF NOT EXISTS team_scores (
            team_name TEXT PRIMARY KEY,
            quiz_score INTEGER DEFAULT 0,
            debug_score INTEGER DEFAULT 0,
            coding_score INTEGER DEFAULT 0,
            total_score INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Quiz questions
        db.execute("""
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            correct_option TEXT
        )
        """)

        # Debug questions
        db.execute("""
        CREATE TABLE IF NOT EXISTS debug_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            buggy_code TEXT,
            keywords TEXT
        )
        """)

        # Coding questions
        db.execute("""
        CREATE TABLE IF NOT EXISTS coding_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            keywords TEXT
        )
        """)

        # Admin
        if not db.execute("SELECT 1 FROM users WHERE username='admin'").fetchone():
            hashed = generate_password_hash("admin123")
            db.execute(
                "INSERT INTO users(username, password, team_name, is_admin) VALUES(?,?,?,?)",
                ("admin", hashed, "Admin", 1)
            )

        # Quiz – 15 questions (fixed: every row has exactly 6 values)
        if not db.execute("SELECT 1 FROM quiz_questions LIMIT 1").fetchone():
            quiz = [
    # Python Questions
    ("Which of the following is used to define a function in Python?", "func", "def", "function", "define", "B"),
    ("Which data type is immutable in Python?", "List", "Tuple", "Dictionary", "Set", "B"),
    ("What is the output of print(2 * 3 ** 2)?", "36", "18", "12", "None", "B"),
    ("Which operator is used for floor division in Python?", "/", "//", "%", "**", "B"),
    ("How do you start a comment in Python?", "//", "#", "/*", "<!--", "B"),
    ("Which of the following is used to take input in Python?", "cin", "scanf", "input()", "read()", "C"),
    ("Which Python keyword is used for conditional branching?", "loop", "if", "case", "switch", "B"),
    ("What will len('Hello World') return?", "10", "11", "12", "None", "B"),
    ("Which of the following is a mutable collection?", "Tuple", "String", "List", "int", "C"),
    ("Which operator checks equality in Python?", "=", "==", "===", "!=", "B"),

    # C Questions
    ("Which of the following is the correct syntax to print in C?", "printf()", "cout", "print()", "echo()", "A"),
    ("Which symbol ends a statement in C?", ".", ";", ":", "!", "B"),
    ("Which operator is used for logical AND in C?", "&", "&&", "||", "!", "B"),
    ("What is the correct syntax for a single-line comment in C?", "// comment", "# comment", "/* comment */", "<!-- comment -->", "A"),
    ("Which data type stores floating-point numbers in C?", "int", "char", "float", "double", "C"),
    ("Which loop executes at least once in C?", "for", "while", "do-while", "foreach", "C"),
    ("Which of the following is used for input in C?", "scanf", "cin", "input()", "read()", "A"),
    ("What is the result of 5 % 2 in C?", "1", "2", "2.5", "0", "A"),
    ("Which header file is required for printf and scanf?", "stdlib.h", "stdio.h", "conio.h", "math.h", "B"),
    ("What is the correct way to declare an integer variable in C?", "int x;", "integer x;", "var x;", "num x;", "A"),

    # Java Questions
    ("Which keyword is used for inheritance in Java?", "inherit", "super", "extends", "this", "C"),
    ("Which of the following is a wrapper class in Java?", "Integer", "int", "String", "double", "A"),
    ("Which operator is used for comparison in Java?", "==", "=", "===", "!=", "A"),
    ("What is the size of int in Java?", "2 bytes", "4 bytes", "8 bytes", "Depends on OS", "B"),
    ("Which method is the entry point of a Java program?", "main()", "start()", "run()", "init()", "A"),
    ("Which keyword prevents inheritance of a class in Java?", "static", "final", "private", "protected", "B"),
    ("Which of the following is used to create objects in Java?", "new", "create", "init", "object", "A"),
    ("Which of the following is true for Java arrays?", "Arrays are immutable", "Arrays can change size dynamically", "Arrays have fixed size", "Arrays cannot store objects", "C"),
    ("Which access modifier makes members accessible only within the same class?", "public", "private", "protected", "default", "B"),
    ("Which keyword is used to handle exceptions in Java?", "try", "catch", "finally", "All of the above", "D")
]


            db.executemany(
                "INSERT INTO quiz_questions(question, option_a, option_b, option_c, option_d, correct_option) VALUES(?,?,?,?,?,?)",
                quiz
            )

        if not db.execute("SELECT 1 FROM debug_questions LIMIT 1").fetchone():

            debug = [
    ("Missing parentheses in print", "print 'Hello World'", "print('Hello World')"),
    ("Unclosed bracket", "lst = [1, 2, 3\nprint(lst)", "]"),
    ("Wrong operator", "if x => 10:\n    print(x)", ">="),
    ("Variable not defined", "print(y)", "y = value"),
    ("Incorrect indentation", "for i in range(5):\nprint(i)", "    print(i)"),
    ("Integer division mistake", "result = 5 / 2", "5 // 2"),
    ("Missing return statement", "def add(a,b):\nc = a+b", "return c"),
    ("C missing semicolon", "int x = 5\nprintf('%d', x);", ";"),
    ("Java wrong method signature", "public static void main(String args) {}", "String[] args"),
    ("Python immutable tuple", "t = (1,2,3)\nt[1] = 5", "Use list instead of tuple")
]

            db.executemany(
    "INSERT INTO debug_questions(title, buggy_code, keywords) VALUES (?,?,?)",
    debug
)

        # Coding – 10 questions with keywords
        if not db.execute("SELECT 1 FROM coding_questions LIMIT 1").fetchone():
            coding = [
    ("Even or Odd", "Check if a number is even or odd", "%, if, else"),
    ("Sum of digits", "Compute the sum of digits of a number", "% 10, // 10, while"),
    ("Palindrome string", "Check if a string is a palindrome", "reverse, ==, slicing"),
    ("Prime check", "Check if a number is prime", "for, range, % i == 0"),
    ("Fibonacci n terms", "Print first n Fibonacci numbers", "loop, a, b, a+b"),
    ("Factorial", "Compute factorial of n", "for, range, multiply"),
    ("Reverse number", "Reverse digits of a number", "while, % 10, // 10"),
    ("Count vowels", "Count vowels in a string", "for, in 'aeiou', if"),
    ("Max in list", "Find maximum number in a list", "max, for, if, >"),
    ("Armstrong number", "Check if a number is an Armstrong number", "while, **, sum")
]
            db.executemany(
                "INSERT INTO coding_questions(title, description, keywords) VALUES(?,?,?)",
                coding
            )

        db.commit()

init_db()

class User(UserMixin):
    def __init__(self, id, username, is_admin, team_name):
        self.id = id
        self.username = username
        self.is_admin = is_admin
        self.team_name = team_name

@login_manager.user_loader
def load_user(user_id):
    with get_db() as db:
        row = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        if row:
            return User(row["id"], row["username"], row["is_admin"], row["team_name"])
    return None

# ─── Routes ─────────────────────────────────────────────

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
            if user and check_password_hash(user["password"], password):
                login_user(User(user["id"], user["username"], user["is_admin"], user["team_name"]))
                flash("Login successful", "success")
                return redirect(url_for("dashboard"))
            flash("Invalid credentials", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        team = request.form.get("team_name")
        if not all([username, password, team]):
            flash("All fields required", "danger")
            return redirect(url_for("register"))
        hashed = generate_password_hash(password)
        try:
            with get_db() as db:
                db.execute("INSERT INTO users(username, password, team_name) VALUES(?,?,?)",
                           (username, hashed, team))
                db.execute("INSERT INTO team_scores(team_name) VALUES(?)", (team,))
                db.commit()
            flash("Registered! Please login.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username or team name taken", "danger")
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out", "info")
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    with get_db() as db:
        row = db.execute("SELECT * FROM team_scores WHERE team_name = ?",
                         (current_user.team_name,)).fetchone()
        score = dict(row) if row else {"quiz_score":0, "debug_score":0, "coding_score":0, "total_score":0}
    return render_template("dashboard.html", score=score, user=current_user)

@app.route("/quiz")
@login_required
def quiz():
    with get_db() as db:
        questions = [dict(row) for row in db.execute("SELECT * FROM quiz_questions LIMIT 30").fetchall()]
    return render_template("quiz.html", questions=questions)

@app.route("/submit_quiz", methods=["POST"])
@login_required
def submit_quiz():
    score = 0
    with get_db() as db:
        correct = {r["id"]: r["correct_option"].upper() 
                   for r in db.execute("SELECT id, correct_option FROM quiz_questions").fetchall()}
        for k, v in request.form.items():
            if k.startswith("q"):
                try:
                    qid = int(k[1:])
                    if qid in correct and v.upper() == correct[qid]:
                        score += 1
                except:
                    pass
        db.execute("""
            UPDATE team_scores
            SET quiz_score = ?,
                total_score = COALESCE(quiz_score,0) + ? + COALESCE(debug_score,0) + COALESCE(coding_score,0),
                updated_at = ?
            WHERE team_name = ?
        """, (score, score, datetime.now(), current_user.team_name))
        db.commit()
    flash(f"Quiz done → {score}/30", "success")
    return redirect(url_for("dashboard"))

@app.route("/debug")
@login_required
def debug():
    with get_db() as db:
        items = [dict(row) for row in db.execute("SELECT id, title, buggy_code FROM debug_questions LIMIT 10").fetchall()]
    return render_template("debug.html", debug_items=items)

@app.route("/submit_debug", methods=["POST"])
@login_required
def submit_debug():
    score = 0
    with get_db() as db:
        questions = db.execute("SELECT id, keywords FROM debug_questions LIMIT 10").fetchall()
        for q in questions:
            code = request.form.get(str(q["id"]), "").lower().strip()
            kws = [k.strip() for k in (q["keywords"] or "").split(",") if k.strip()]
            matched = sum(1 for kw in kws if kw in code)
            if matched >= max(1, len(kws) // 2 + 1):
                score += 1
        db.execute("""
            UPDATE team_scores
            SET debug_score = ?,
                total_score = COALESCE(quiz_score,0) + ? + COALESCE(coding_score,0),
                updated_at = ?
            WHERE team_name = ?
        """, (score, score, datetime.now(), current_user.team_name))
        db.commit()
    flash(f"Debug → {score}/10", "success")
    return redirect(url_for("dashboard"))

@app.route("/coding")
@login_required
def coding():
    with get_db() as db:
        prompts = [dict(row) for row in db.execute("SELECT id, title, description, keywords FROM coding_questions LIMIT 10").fetchall()]
    return render_template("coding.html", coding_prompts=prompts)

@app.route("/submit_coding", methods=["POST"])
@login_required
def submit_coding():
    score = 0
    with get_db() as db:
        questions = db.execute("SELECT id, keywords FROM coding_questions LIMIT 10").fetchall()
        for q in questions:
            code = request.form.get(f"code_{q['id']}", "").lower().strip()
            kws = [k.strip() for k in (q["keywords"] or "").split(",") if k.strip()]
            matched = sum(1 for kw in kws if kw in code)
            if matched >= max(1, len(kws) // 2):
                score += 1
        db.execute("""
            UPDATE team_scores
            SET coding_score = ?,
                total_score = COALESCE(quiz_score,0) + COALESCE(debug_score,0) + ?,
                updated_at = ?
            WHERE team_name = ?
        """, (score, score, datetime.now(), current_user.team_name))
        db.commit()
    flash(f"Coding → {score}/10", "success")
    return redirect(url_for("dashboard"))

@app.route("/leaderboard")
def leaderboard():
    with get_db() as db:
        rows = db.execute("""
            SELECT team_name, quiz_score, debug_score, coding_score, total_score
            FROM team_scores
            WHERE total_score > 0
            ORDER BY total_score DESC
            LIMIT 10
        """).fetchall()
        rankings = [dict(row) for row in rows]

    return render_template(
        "leaderboard.html",
        rankings=rankings,
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
    )

@app.route("/admin")
@login_required
def admin():
    if not current_user.is_admin:
        flash("Admin only", "danger")
        return redirect(url_for("dashboard"))
    with get_db() as db:
        scores = [dict(row) for row in db.execute("SELECT * FROM team_scores ORDER BY total_score DESC").fetchall()]
    return render_template("admin.html", scores=scores)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
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

DB_PATH = os.path.join(os.path.dirname(__file__), "database2.db")

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
                ("Which keyword defines function in Python?", "func", "def", "function", "define", "B"),
                ("Output of 5 // 2 ?", "2.5", "2", "3", "error", "B"),
                ("Print function in C?", "scanf", "printf", "print", "cout", "B"),
                ("Java inheritance keyword?", "extends", "inherit", "super", "this", "A"),
                ("Immutable Python collection?", "List", "Tuple", "Set", "Dictionary", "B"),
                ("Equality operator Python?", "=", "==", "===", "!=", "B"),
                ("FIFO structure?", "Stack", "Queue", "List", "Array", "B"),
                ("len('BCA')?", "2", "3", "4", "5", "C"),
                ("Conditional keyword?", "loop", "if", "case", "switch", "B"),
                ("2 ** 3 result?", "6", "8", "9", "4", "B"),
                ("Loop runs once?", "for", "while", "do while", "foreach", "C"),
                ("Key value collection?", "List", "Tuple", "Dictionary", "Set", "C"),
                ("print(10>5)?", "True", "False", "0", "Error", "A"),
                ("End of C statement?", ";", ":", "!", "?", "A"),
                ("Logical AND in C?", "&", "&&", "||", "!", "B")
            ]
            db.executemany(
                "INSERT INTO quiz_questions(question, option_a, option_b, option_c, option_d, correct_option) VALUES(?,?,?,?,?,?)",
                quiz
            )

        if not db.execute("SELECT 1 FROM debug_questions LIMIT 1").fetchone():

            debug = [
("Missing colon in if","if x > 5\n    print(x)","if x > 5:"),
("Unclosed string","print('Hello)","'Hello'"),
("Missing semicolon","printf('Hi')",";"),
("Wrong indentation","def func():\nprint('hi')","    print"),
("== vs =","if a = 5:","=="),
("List index error","lst = [1,2,3]\nprint(lst[3])","[2]"),
("No return type","int add(a, b) { return a+b }","int a"),
("Java class mismatch","public class hello {","Hello"),
("C pointer wrong","int *p = 10;","&"),
("Python tuple mutable","t = (1,2)\nt[0] = 5","list")
]

            db.executemany(
    "INSERT INTO debug_questions(title, buggy_code, keywords) VALUES (?,?,?)",
    debug
)

        # Coding – 10 questions with keywords
        if not db.execute("SELECT 1 FROM coding_questions LIMIT 1").fetchone():
            coding = [
                ("Even or Odd", "Check if number is even or odd", "%, even, odd"),
                ("Sum of digits", "Sum digits of number", "% 10, // 10"),
                ("Palindrome string", "Check string palindrome", "reverse, ==, slicing"),
                ("Prime check", "Check if number is prime", "for, range, % i == 0"),
                ("Fibonacci n terms", "Print first n Fibonacci", "loop, a b, a+b"),
                ("Factorial", "Compute n!", "for, range, multiply"),
                ("Reverse number", "Reverse digits", "while, % 10, // 10"),
                ("Count vowels", "Count vowels in string", "for, in 'aeiou'"),
                ("Max in list", "Find max number in list", "max, for, >"),
                ("Armstrong number", "Check Armstrong number", "while, ** 3, sum")
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
        questions = [dict(row) for row in db.execute("SELECT * FROM quiz_questions LIMIT 15").fetchall()]
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
    flash(f"Quiz done → {score}/15", "success")
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
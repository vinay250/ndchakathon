# CodeCraft 2026 – National Degree College BCA Hackathon System

A simple web-based platform for conducting a team-based coding competition with three rounds:  
- **Quiz Round** (15 MCQ questions)  
- **Debug Round** (10 debugging problems)  
- **Coding Round** (10 programming problems)  

Teams register, participate in rounds, earn scores, and view their rank on a live leaderboard.

## Features

- User registration & login (team-based)
- Admin panel (username: `admin`, password: `admin123`)
- Three competition rounds:
  - Quiz: 15 multiple-choice questions (Python, C, Java)
  - Debug: 10 buggy code snippets to fix
  - Coding: 10 programming problems
- Automatic score calculation and total score update
- Live leaderboard showing top teams by total score
- Responsive Bootstrap interface
- SQLite database (no external DB required)

## Tech Stack

- **Backend**: Flask (Python)
- **Authentication**: Flask-Login
- **Database**: SQLite (file-based)
- **Frontend**: Bootstrap 5 + Bootstrap Icons
- **Templating**: Jinja2

## Project Structure
hackathon_system/
├── app.py                    # Main Flask application
├── database.db               # SQLite database (auto-created)
└── templates/
├── base.html             # Base layout (Bootstrap + navbar)
├── login.html
├── register.html
├── dashboard.html        # Shows team scores + links to rounds
├── quiz.html             # 15-question MCQ quiz
├── debug.html            # 10 debugging problems
├── coding.html           # 10 coding problems
├── leaderboard.html      # Live ranking table
└── admin.html            # Admin view of all teams' scores

### Screenshots
![Screenshot 1](1.png)
![Screenshot 2](2.png)
![Screenshot 3](3.png)
![Screenshot 4](4.png)
![Screenshot 5](5.png)
![Screenshot 6](6.png)
![Screenshot 6](7.png)
## Installation & Setup

### Prerequisites

- Python 3.8+
- pip

### Steps

1. Clone or download the project

```bash
git clone <your-repo-url>
cd hackathon_system

Install dependencies

Bashpip install flask flask-login werkzeug

(Optional) Delete old database if you want fresh start

Bashrm database.db   # Linux/Mac
del database.db  # Windows

Run the application

Bashpython app.py

Open in browser

texthttp://localhost:5000
Default Credentials

Admin:
Username: admin
Password: admin123
Register new teams via /register

How to Use

Register a team at /register
Login with team credentials
Go to Dashboard — see current scores + buttons to start rounds
Complete:
Quiz → answer 15 MCQs → submit
Debug → fix 10 buggy codes → submit
Coding → solve 10 problems → submit

View your updated scores on Dashboard
Check team ranking on Leaderboard (/leaderboard)

Scoring Rules (Simple Version)

Quiz: 1 point per correct MCQ answer (out of 15)
Debug: 1 point if submitted answer contains expected keywords or is long enough
Coding: 1 point if submitted code contains expected keywords or is long enough
Total Score = Quiz + Debug + Coding

Admin Features

Login as admin
Go to /admin to see all teams' scores
(Future: add manual score editing if needed)

Future Improvements (Ideas)

Add time limits per round
Prevent multiple submissions
Better code evaluation (keyword patterns → basic judge)
Export leaderboard as PDF/CSV
Team member login (multiple users per team)
Real-time leaderboard updates (WebSocket / polling)

License
MIT License – feel free to use, modify, and share for educational/hackathon purposes.
Made with ❤️ for National Degree College BCA Hackathon 2026
textYou can copy this entire content and save it as **`README.md`** in your project root folder.

If you want any section changed (e.g., add screenshots, change project name, add team credits, etc.), just tell me — I'll update it quickly.  

Happy hacking! 🚀
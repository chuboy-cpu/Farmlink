# Farmer's LinkUp - Flask prototype

Simplified prototype (Flask + Jinja + Bootstrap 5). No database: data is held in memory
and resets whenever the server restarts. Any email/password works at login.

## Run

    python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    python app.py
Open <http://127.0.0.1:5000>

## Flow

Landing -> Sign up / Log in -> Home -> Produce (list new) -> Requests (accept/decline)
-> Review & confirm -> Sales (weigh & sign off -> paid) -> Account

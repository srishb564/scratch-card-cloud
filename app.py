import os
import uuid
import random
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

# =========================
# DATABASE CONFIG
# =========================
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def get_conn():
    return psycopg2.connect(os.environ["DATABASE_URL"])

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scratch_cards (
            id UUID PRIMARY KEY,
            card_name TEXT NOT NULL,
            reward TEXT NOT NULL,
            link TEXT NOT NULL,
            scratched BOOLEAN DEFAULT FALSE
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Initialize DB on startup
init_db()

# =========================
# HOME – GENERATE SCRATCH CARD
# =========================
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        card_name = request.form.get("card_name")
        if not card_name:
            return "card_name missing", 400

        try:
            card_id =str(uuid.uuid4())
            reward = random.choice(["₹50", "₹100", "Better Luck Next Time"])
            link = request.host_url.rstrip("/") + "/scratch/" + str(card_id)

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO scratch_cards (id, card_name, reward, link, scratched)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (card_id, card_name, reward, link, False)
            )
            conn.commit()
            cur.close()
            conn.close()

        except Exception as e:
            return f"Database error: {e}", 500

        return redirect(url_for("index"))

    return render_template("index.html")


# =========================
# SCRATCH CARD PAGE
# =========================
@app.route("/scratch/<uuid:card_id>")
def scratch(card_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT reward, scratched FROM scratch_cards WHERE id = %s",
        (card_id,)
    )
    data = cur.fetchone()
    cur.close()
    conn.close()

    if not data:
        return "Invalid or expired scratch card"

    reward, scratched = data

    return render_template(
        "scratch.html",
        reward=reward,
        card_id=str(card_id),
        scratched=scratched
    )

# =========================
# MARK AS SCRATCHED (60%)
# =========================
@app.route("/mark-scratched/<uuid:card_id>", methods=["POST"])
def mark_scratched(card_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE scratch_cards SET scratched = TRUE WHERE id = %s",
        (card_id,)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "success"})

# =========================
# ADMIN PANEL
# =========================
@app.route("/admin")
def admin():
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT card_name, reward, link, scratched
            FROM scratch_cards
            ORDER BY card_name
        """)

        rows = cur.fetchall()

        cur.close()
        conn.close()

        html = """
        <h1>Scratch Card Admin Panel</h1>
        <table border="1" cellpadding="8">
            <tr>
                <th>Card Name</th>
                <th>Reward</th>
                <th>Link</th>
                <th>Scratched</th>
            </tr>
        """

        for r in rows:
            html += f"""
            <tr>
                <td>{r[0]}</td>
                <td>{r[1]}</td>
                <td><a href="{r[2]}" target="_blank">{r[2]}</a></td>
                <td>{r[3]}</td>
            </tr>
            """

        html += "</table>"
        return html

    except Exception as e:
        return f"Admin error: {str(e)}", 500



# =========================
# HEALTH CHECK (OPTIONAL)
# =========================
@app.route("/health")
def health():
    return "OK"

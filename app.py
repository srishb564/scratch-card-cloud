from flask import Flask, render_template, request, redirect, url_for, jsonify
import psycopg2
import os
import uuid
import random

app = Flask(__name__)

# --------------------------------------------------
# DATABASE CONNECTION (SINGLE SOURCE OF TRUTH)
# --------------------------------------------------
def get_db():
    return psycopg2.connect(
        os.environ["DATABASE_URL"],
        sslmode="require"
    )

# --------------------------------------------------
# HOME PAGE – GENERATE SCRATCH CARD
# --------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        card_name = request.form.get("card_name")

        rewards = ["₹50", "₹100", "Better Luck Next Time"]
        reward = random.choice(rewards)

        card_id = str(uuid.uuid4())
        link = request.url_root + "scratch/" + card_id

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO scratch_cards (id, card_name, reward, link, scratched)
            VALUES (%s, %s, %s, %s, FALSE)
        """, (card_id, card_name, reward, link))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("admin"))

    return render_template("index.html")

# --------------------------------------------------
# SCRATCH CARD PAGE
# --------------------------------------------------
@app.route("/scratch/<card_id>")
def scratch(card_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT card_name, reward, scratched
        FROM scratch_cards
        WHERE id = %s
    """, (card_id,))

    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return "Invalid or expired scratch card", 404

    return render_template(
        "scratch.html",
        card_name=row[0],
        reward=row[1],
        scratched=row[2],
        card_id=card_id
    )

# --------------------------------------------------
# MARK CARD AS SCRATCHED (CRITICAL ROUTE)
# --------------------------------------------------
@app.route("/mark_scratched/<card_id>", methods=["POST"])
def mark_scratched(card_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE scratch_cards
        SET scratched = TRUE
        WHERE id = %s
    """, (card_id,))

    updated_rows = cur.rowcount
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({
        "status": "ok",
        "updated_rows": updated_rows
    })

# --------------------------------------------------
# ADMIN PANEL
# --------------------------------------------------
@app.route("/admin")
def admin():
    conn = get_db()
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
    <h1>Admin Panel</h1>
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

# --------------------------------------------------
# MAIN
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)

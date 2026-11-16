from flask import Flask, redirect, render_template, request, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = "database.db"


# Database connection helper
def get_db_connection():
  conn = sqlite3.connect(DB_NAME)
  conn.row_factory = sqlite3.Row  # Columns ko name se access karne ke liye
  return conn


# Database aur table initialize karne ke liye function
def init_db():
  conn = get_db_connection()
  conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            remarks TEXT DEFAULT '-'
        )
    """)
  # Agar table khali hai toh kuch sample leads dal dein
  cursor = conn.execute("SELECT COUNT(*) FROM leads")
  if cursor.fetchone()[0] == 0:
    conn.executemany(
        "INSERT INTO leads (name, phone, status, remarks) VALUES (?, ?, ?, ?)",
        [
            ("Rahul Sharma", "9876543210", "Pending", "-"),
            ("Priya Verma", "9123456789", "Interested", "Call back tomorrow"),
            ("Amit Kumar", "9988776655", "Not Interested", "Budget issue"),
        ],
    )
  conn.commit()
  conn.close()


@app.route("/")
def dashboard():
  conn = get_db_connection()
  leads = conn.execute("SELECT * FROM leads").fetchall()
  conn.close()
  return render_template("index.html", leads=leads)


# Naya Lead Add karne ke liye route
@app.route("/add", methods=["POST"])
def add_lead():
  name = request.form.get("name")
  phone = request.form.get("phone")
  if name and phone:
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO leads (name, phone, status, remarks) VALUES (?, ?, "
        "'Pending', '-')",
        (name, phone),
    )
    conn.commit()
    conn.close()
  return redirect(url_for("dashboard"))


# Lead Status aur Remarks update karne ke liye route
@app.route("/update/<int:lead_id>", methods=["POST"])
def update_lead(lead_id):
  new_status = request.form.get("status")
  new_remarks = request.form.get("remarks")

  conn = get_db_connection()
  conn.execute(
      "UPDATE leads SET status = ?, remarks = ? WHERE id = ?",
      (new_status, new_remarks, lead_id),
  )
  conn.commit()
  conn.close()
  return redirect(url_for("dashboard"))


if __name__ == "__main__":
  init_db()  # Server start hone se pehle database setup karein
  app.run(debug=True)
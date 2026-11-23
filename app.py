import sqlite3
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_NAME = "tickets.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open',
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "Support Ticket REST API"}), 200


@app.route("/tickets", methods=["GET"])
def get_tickets():
    status_filter = request.args.get("status")
    with get_db_connection() as conn:
        if status_filter:
            rows = conn.execute(
                "SELECT * FROM tickets WHERE status = ?", (status_filter,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM tickets").fetchall()

    tickets = [dict(row) for row in rows]
    return jsonify({"count": len(tickets), "tickets": tickets}), 200


@app.route("/tickets", methods=["POST"])
def create_ticket():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    severity = data.get("severity", "medium").lower()

    if not title:
        return jsonify({"error": "Field 'title' is required."}), 400

    if severity not in {"low", "medium", "high", "critical"}:
        return jsonify({"error": "Severity must be low, medium, high, or critical."}), 400

    created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    with get_db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO tickets (title, severity, status, created_at) VALUES (?, ?, ?, ?)",
            (title, severity, "open", created_at),
        )
        conn.commit()
        ticket_id = cursor.lastrowid

    return jsonify(
        {
            "message": "Ticket created",
            "ticket": {
                "id": ticket_id,
                "title": title,
                "severity": severity,
                "status": "open",
                "created_at": created_at,
            },
        }
    ), 201


@app.route("/tickets/<int:ticket_id>/resolve", methods=["PATCH"])
def resolve_ticket(ticket_id):
    with get_db_connection() as conn:
        cursor = conn.execute(
            "UPDATE tickets SET status = 'resolved' WHERE id = ?", (ticket_id,)
        )
        conn.commit()

    if cursor.rowcount == 0:
        return jsonify({"error": f"Ticket ID {ticket_id} not found."}), 404

    return jsonify({"message": f"Ticket {ticket_id} marked as resolved."}), 200


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)

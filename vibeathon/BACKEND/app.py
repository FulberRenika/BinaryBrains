from flask import Flask, request, jsonify, render_template
from datetime import datetime
import uuid

app = Flask(__name__)

# In-memory store (enough for demo)
cases = {}

STATUSES = [
    "Request Received",
    "Preparing",
    "Team Dispatched",
    "On the Way",
    "Action in Progress",
    "Resolved"
]

def classify_emergency(text: str):
    t = text.lower()

    departments = set()

    fire_kw = ["fire", "smoke", "burn", "burning", "gas leak", "explosion"]
    amb_kw  = ["accident", "injury", "blood", "bleeding", "unconscious", "faint", "breathing", "heart", "stroke"]
    pol_kw  = ["theft", "robbery", "attack", "fight", "threat", "weapon", "knife", "gun", "harassment"]

    if any(k in t for k in fire_kw):
        departments.add("Fire Station")
    if any(k in t for k in amb_kw):
        departments.add("Ambulance")
    if any(k in t for k in pol_kw):
        departments.add("Police")

    if not departments:
        # fallback: if unclear, send Police (common emergency intake)
        departments.add("Police")

    # Severity
    critical_kw = ["not breathing", "unconscious", "explosion", "severe bleeding", "big fire", "collapsed"]
    high_kw     = ["fire", "accident", "weapon", "knife", "gun", "gas leak"]
    medium_kw   = ["bleeding", "injury", "theft", "fight"]
    low_kw      = ["noise", "lost", "minor", "small"]

    if any(k in t for k in critical_kw):
        severity = "Critical"
    elif any(k in t for k in high_kw):
        severity = "High"
    elif any(k in t for k in medium_kw):
        severity = "Medium"
    elif any(k in t for k in low_kw):
        severity = "Low"
    else:
        severity = "Medium"

    return sorted(list(departments)), severity

def build_alert_message(case_id, text, departments, severity, has_media):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    media_note = "Media attached: Yes" if has_media else "Media attached: No"
    dept_str = ", ".join(departments)

    msg = (
        f"[ALERT ID: {case_id}]\n"
        f"Timestamp: {ts}\n"
        f"Departments: {dept_str}\n"
        f"Severity: {severity}\n"
        f"{media_note}\n"
        f"User Report: {text.strip()}\n"
        f"Action: Dispatch nearest available team immediately."
    )
    return msg, ts

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    text = request.form.get("description", "")
    file = request.files.get("media")
    has_media = bool(file and file.filename)

    case_id = str(uuid.uuid4())[:8]
    departments, severity = classify_emergency(text)
    message, ts = build_alert_message(case_id, text, departments, severity, has_media)

    cases[case_id] = {
        "created_at": ts,
        "status_index": 0,
        "departments": departments,
        "severity": severity,
        "message": message
    }

    return jsonify({
        "case_id": case_id,
        "departments": departments,
        "severity": severity,
        "message": message,
        "timestamp": ts
    })

@app.route("/status/<case_id>")
def status(case_id):
    c = cases.get(case_id)
    if not c:
        return jsonify({"error": "Not found"}), 404

    # advance status each time user checks (demo simulation)
    if c["status_index"] < len(STATUSES) - 1:
        c["status_index"] += 1

    return jsonify({
        "case_id": case_id,
        "status": STATUSES[c["status_index"]]
    })

if __name__ == "__main__":
    app.run(debug=True)

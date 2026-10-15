import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from api.auth import auth_bp
from api.dashboard import dashboard_bp
from api.tickets import ticket_bp
from api.technician import technician_bp
from api.management import management_bp
from api.admin import admin_bp   # ← sẽ tạo mới


load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

CORS(
    app,
    supports_credentials=True,
    origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
)

app.register_blueprint(auth_bp,       url_prefix="/auth")
app.register_blueprint(dashboard_bp,  url_prefix="/api")
app.register_blueprint(ticket_bp,     url_prefix="/tickets")
app.register_blueprint(technician_bp, url_prefix="/technician")
app.register_blueprint(management_bp, url_prefix="/management")
app.register_blueprint(admin_bp,      url_prefix="/admin")


@app.get("/")
def health():
    return jsonify({"ok": True, "service": "neu-helpdesk-backend"})


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)

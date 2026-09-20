import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from api.auth import auth_bp


load_dotenv()


app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

CORS(
    app,
    supports_credentials=True
)


app.register_blueprint(
    auth_bp,
    url_prefix="/auth"
)


if __name__ == "__main__":
    app.run(debug=True)
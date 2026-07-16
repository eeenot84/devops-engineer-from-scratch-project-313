import os

import sentry_sdk
from flask import Flask
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FlaskIntegration()],
    )

DATABASE_URL = os.getenv("DATABASE_URL")

app = Flask(__name__)


@app.route("/ping")
def ping():
    return "pong"


@app.route("/error")
def error():
    raise RuntimeError("Oops! Something went wrong!")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)

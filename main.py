import json
import os
import re

import sentry_sdk
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, request
from flask_cors import CORS
from sentry_sdk.integrations.flask import FlaskIntegration
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from database import get_session, init_db, reset_engine
from models import Link, LinkCreate, LinkUpdate, link_to_read

load_dotenv()

DUPLICATE_SHORT_NAME = {"error": "Entity with short_name already exists"}
RANGE_RE = re.compile(r"^\[\s*(-?\d+)\s*,\s*(-?\d+)\s*\]$")
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]


def parse_range(raw: str | None) -> tuple[int, int] | None:
    """Parse range=[start, end]. End is exclusive (как в примерах задания)."""
    if raw is None or raw == "":
        return None
    match = RANGE_RE.match(raw.strip())
    if match:
        return int(match.group(1)), int(match.group(2))
    try:
        start, end = json.loads(raw)
        return int(start), int(end)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None


def create_app() -> Flask:
    reset_engine()

    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FlaskIntegration()],
        )

    app = Flask(__name__)
    CORS(
        app,
        resources={r"/*": {"origins": CORS_ORIGINS}},
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "Range"],
        expose_headers=["Content-Range", "Accept-Ranges"],
        supports_credentials=True,
    )
    init_db()

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Not Found"}), 404

    @app.get("/ping")
    def ping():
        return "pong"

    @app.get("/error")
    def trigger_error():
        raise RuntimeError("Oops! Something went wrong!")

    @app.get("/r/<short_name>")
    def redirect_short_link(short_name: str):
        with get_session() as session:
            link = session.exec(
                select(Link).where(Link.short_name == short_name)
            ).first()
            if link is None:
                return jsonify({"error": "Not Found"}), 404
            return redirect(link.original_url, code=302)

    @app.get("/api/links")
    def list_links():
        with get_session() as session:
            links = session.exec(select(Link).order_by(Link.id)).all()
            total = len(links)
            parsed = parse_range(request.args.get("range"))
            if parsed is None:
                start, end = 0, total
                page = links
            else:
                start, end = parsed
                if start < 0:
                    start = 0
                if end < start:
                    end = start
                page = links[start:end]

            response = jsonify([link_to_read(link) for link in page])
            response.headers["Content-Range"] = f"links {start}-{end}/{total}"
            response.headers["Accept-Ranges"] = "links"
            response.status_code = 200
            return response

    @app.post("/api/links")
    def create_link():
        payload = request.get_json(silent=True) or {}
        data = LinkCreate.model_validate(payload)
        link = Link(original_url=data.original_url, short_name=data.short_name)
        with get_session() as session:
            session.add(link)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                return jsonify(DUPLICATE_SHORT_NAME), 409
            session.refresh(link)
            return jsonify(link_to_read(link)), 201

    @app.get("/api/links/<int:link_id>")
    def get_link(link_id: int):
        with get_session() as session:
            link = session.get(Link, link_id)
            if link is None:
                return jsonify({"error": "Not Found"}), 404
            return jsonify(link_to_read(link)), 200

    @app.put("/api/links/<int:link_id>")
    def update_link(link_id: int):
        payload = request.get_json(silent=True) or {}
        data = LinkUpdate.model_validate(payload)
        with get_session() as session:
            link = session.get(Link, link_id)
            if link is None:
                return jsonify({"error": "Not Found"}), 404
            link.original_url = data.original_url
            link.short_name = data.short_name
            session.add(link)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                return jsonify(DUPLICATE_SHORT_NAME), 409
            session.refresh(link)
            return jsonify(link_to_read(link)), 200

    @app.delete("/api/links/<int:link_id>")
    def delete_link(link_id: int):
        with get_session() as session:
            link = session.get(Link, link_id)
            if link is None:
                return jsonify({"error": "Not Found"}), 404
            session.delete(link)
            session.commit()
            return ("", 204)

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)

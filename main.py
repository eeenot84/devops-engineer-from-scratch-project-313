import os

import sentry_sdk
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from sentry_sdk.integrations.flask import FlaskIntegration
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from database import get_session, init_db, reset_engine
from models import Link, LinkCreate, LinkUpdate, link_to_read

load_dotenv()

DUPLICATE_SHORT_NAME = {"error": "Entity with short_name already exists"}


def create_app() -> Flask:
    reset_engine()

    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FlaskIntegration()],
        )

    app = Flask(__name__)
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

    @app.get("/api/links")
    def list_links():
        with get_session() as session:
            links = session.exec(select(Link).order_by(Link.id)).all()
            return jsonify([link_to_read(link) for link in links]), 200

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

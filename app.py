import os

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from flask_mail import Mail, Message

from locale_loader import load_server_messages

load_dotenv()

MAX_QUESTION_LENGTH = 2000
DEFAULT_CHAT_API_URL = "http://localhost:8080/api/v1/chat"
DEFAULT_CHAT_QUESTION_LIMIT = 7
DEFAULT_CHAT_REQUEST_TIMEOUT = 120

MESSAGES = load_server_messages()


def get_locale():
    """Resolve the visitor locale from cookie or Accept-Language header."""
    locale = request.cookies.get("locale", "")
    if locale in MESSAGES:
        return locale
    accept_language = request.headers.get("Accept-Language", "")
    if accept_language.lower().startswith("pt"):
        return "pt-BR"
    return "en"


def message(key):
    """Return a localized message for the current request locale."""
    return MESSAGES.get(get_locale(), MESSAGES["en"]).get(key, MESSAGES["en"][key])


def get_chat_quota():
    """Return used, limit, and remaining question counts for the current session."""
    used = session.get("chat_questions_used", 0)
    limit = current_app.config["CHAT_QUESTION_LIMIT"]
    remaining = max(limit - used, 0)
    return used, limit, remaining


def create_app():
    """Create and configure the Flask application."""
    application = Flask(__name__)

    application.config["CHAT_API_URL"] = os.getenv("CHAT_API_URL", DEFAULT_CHAT_API_URL)
    application.config["CHAT_QUESTION_LIMIT"] = int(
        os.getenv("CHAT_QUESTION_LIMIT", str(DEFAULT_CHAT_QUESTION_LIMIT))
    )
    application.config["CHAT_REQUEST_TIMEOUT"] = int(
        os.getenv("CHAT_REQUEST_TIMEOUT", str(DEFAULT_CHAT_REQUEST_TIMEOUT))
    )
    application.config["SECRET_KEY"] = os.getenv("secret_key")
    application.config["MAIL_SERVER"] = "smtp.gmail.com"
    application.config["MAIL_PORT"] = 587
    application.config["MAIL_USE_TLS"] = True
    application.config["MAIL_USERNAME"] = "guilhermelc10@gmail.com"
    application.config["MAIL_PASSWORD"] = os.getenv("senha_email")
    mail = Mail(application)

    @application.route("/", methods=["GET", "POST"])
    def home():
        if request.method == "POST":
            nome = request.form["nome"]
            email = request.form["email"]
            telefone = request.form["telefone"]
            assunto = request.form["assunto"]
            mensagem = request.form["mensagem"]

            if not nome or not telefone or not assunto or not mensagem:
                flash(message("fill_fields"), "error")
                return redirect(url_for("home"))

            msg = Message(
                subject=f"Contato: {assunto}",
                sender=application.config["MAIL_USERNAME"],
                recipients=["guilhermelc10@gmail.com"],
                body=f"""
Nome: {nome}
E-mail:{email}
Telefone: {telefone}
Assunto: {assunto}

Mensagem:
{mensagem}
                      """,
            )
            try:
                mail.send(msg)
                flash(message("email_success"), "success")
            except Exception:
                flash(message("email_error"), "error")

            return redirect(url_for("home"))

        chat_config = {
            "endpoint": "/api/chat",
            "statusEndpoint": "/api/chat/status",
            "questionLimit": application.config["CHAT_QUESTION_LIMIT"],
            "timeoutMs": application.config["CHAT_REQUEST_TIMEOUT"] * 1000,
        }
        return render_template("home.html", chat_config=chat_config)

    @application.route("/download/<filename>")
    def download_file(filename):
        directory = os.path.join(os.path.dirname(__file__), "cv")
        return send_from_directory(directory, filename, as_attachment=True)

    @application.route("/api/chat/status", methods=["GET"])
    def chat_status():
        used, limit, remaining = get_chat_quota()
        return jsonify({"used": used, "limit": limit, "remaining": remaining})

    @application.route("/api/chat", methods=["POST"])
    def chat_proxy():
        used, limit, _remaining = get_chat_quota()
        if used >= limit:
            return jsonify({"error": message("chat_limit_reached"), "remaining": 0}), 429

        payload = request.get_json(silent=True) or {}
        question = (payload.get("question") or "").strip()
        if not question:
            return jsonify({"error": message("chat_empty_question")}), 400
        if len(question) > MAX_QUESTION_LENGTH:
            return jsonify({"error": message("chat_empty_question")}), 400

        try:
            upstream = requests.post(
                current_app.config["CHAT_API_URL"],
                json={"question": question},
                timeout=current_app.config["CHAT_REQUEST_TIMEOUT"],
            )
            upstream.raise_for_status()
            data = upstream.json()
            answer = data.get("answer", "")
        except requests.Timeout:
            return jsonify({"error": message("chat_timeout")}), 504
        except (requests.RequestException, ValueError, TypeError):
            return jsonify({"error": message("chat_unavailable")}), 503

        session["chat_questions_used"] = used + 1
        _, _, remaining_after = get_chat_quota()
        return jsonify({"answer": answer, "remaining": remaining_after})

    return application


app = create_app()

if __name__ == "__main__":
    app.run()
from flask import Blueprint, request, jsonify, render_template
from app.services.context_service import context_service
from app.services.llm_service import llm_service

chat_bp = Blueprint('chat', __name__)

@chat_bp.route("/")
def index():
    return render_template("index.html")

@chat_bp.route("/get-response", methods=["POST"])
def get_response():
    try:
        data = request.get_json()
        user_input = data["message"]

        messages = context_service.get_context_messages()
        messages.append({"role": "user", "content": user_input})
        result = llm_service.generate_response(messages)
        context_service.update_context(user_input, result)

        return jsonify({"reply": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route("/reset", methods=["POST"])
def reset_context():
    context_service.reset_context()
    return jsonify({"status": "contexto reiniciado"})
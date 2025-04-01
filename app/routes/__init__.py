from app.routes.chat_routes import chat_bp

def register_blueprints(app):
    app.register_blueprint(chat_bp)

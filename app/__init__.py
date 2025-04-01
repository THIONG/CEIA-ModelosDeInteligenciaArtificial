from flask import Flask
from flask_cors import CORS
from app.routes import register_blueprints

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # Configurar CORS
    CORS(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    return app

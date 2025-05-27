from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

from api.routes.auth import auth_bp
from api.routes.usuarios import usuarios_bp
from api.routes.empresas import empresas_bp
from api.routes.grupos import grupos_bp
from api.routes.eventos import eventos_bp
from api.routes.calendario import calendario_bp
from api.database.models import init_db

# Carrega variáveis de ambiente
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL', 'sqlite:///./database/app.db')
    
    # CORS
    CORS(app)
    
    # Inicializa banco de dados
    init_db(app.config['DATABASE_URL'])
    
    # Registra blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(usuarios_bp, url_prefix='/api/usuarios')
    app.register_blueprint(empresas_bp, url_prefix='/api/empresas')
    app.register_blueprint(grupos_bp, url_prefix='/api/grupos')
    app.register_blueprint(eventos_bp, url_prefix='/api/eventos')
    app.register_blueprint(calendario_bp, url_prefix='/api/calendario')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)

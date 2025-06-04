from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

from api.routes.auth import auth_bp
from api.routes.usuarios import usuarios_bp
from api.routes.empresas import empresas_bp
from api.routes.grupos import grupos_bp
from api.routes.eventos import eventos_bp
from api.routes.tipos_ausencia import tipos_ausencia_bp
from api.routes.turnos import turnos_bp
from api.routes.ufs import ufs_bp
from api.routes.feriados import feriados_bp
from api.database.models import init_db

# Carrega variáveis de ambiente
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # CORS
    CORS(app)
    
    # Configuração do banco de dados com fallback
    database_url = None
    
    # Tenta configurar MySQL primeiro
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASS')
    
    if all([db_host, db_name, db_user, db_pass]):
        database_url = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        print("🔄 Tentando conectar ao MySQL na GCP...")
    else:
        print("⚠️  Credenciais MySQL não encontradas, usando SQLite")
    
    app.config['DATABASE_URL'] = database_url
    
    # Inicializa banco de dados (com fallback automático)
    init_db(database_url)
    
    # Health check endpoint
    @app.route('/')
    def health_check():
        return jsonify({
            "status": "API Flask funcionando!",
            "database": "MySQL" if database_url and database_url.startswith("mysql") else "SQLite",
            "version": "2.0"
        })
    
    # Registra blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(usuarios_bp, url_prefix='/api/usuarios')
    app.register_blueprint(empresas_bp, url_prefix='/api/empresas')
    app.register_blueprint(grupos_bp, url_prefix='/api/grupos')
    app.register_blueprint(eventos_bp, url_prefix='/api/eventos')
    app.register_blueprint(tipos_ausencia_bp, url_prefix='/api/tipos-ausencia')
    app.register_blueprint(turnos_bp, url_prefix='/api/turnos')
    app.register_blueprint(ufs_bp, url_prefix='/api/ufs')
    app.register_blueprint(feriados_bp, url_prefix='/api/feriados')
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Informações de inicialização
    db_host = os.getenv('DB_HOST')
    if db_host:
        print(f"📊 Tentativa de conexão MySQL: {db_host}")
        print(f"🗄️  Database: {os.getenv('DB_NAME')}")
    
    print("🔄 Nova estrutura de schema implementada!")
    print("🌐 Servidor iniciando na porta 5000...")
    
    app.run(debug=True, port=5000)

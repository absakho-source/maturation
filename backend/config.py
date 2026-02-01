import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Déterminer l'URI de la base de données
# En production (Render): utilise DATABASE_URL (PostgreSQL)
# En local: utilise SQLite par défaut
_database_url = os.environ.get('DATABASE_URL')
if _database_url:
    # Render fournit 'postgres://' mais SQLAlchemy 2.x exige 'postgresql://'
    if _database_url.startswith('postgres://'):
        _database_url = _database_url.replace('postgres://', 'postgresql://', 1)
    _default_db_uri = _database_url
else:
    _default_db_uri = f"sqlite:///{os.path.join(BASE_DIR, 'maturation.db')}"

class Config:
    SECRET_KEY = "dev-secret"
    SQLALCHEMY_DATABASE_URI = _default_db_uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    PROPAGATE_EXCEPTIONS = True

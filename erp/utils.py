import sqlalchemy as sqla
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
load_dotenv()


def encrypt_password(data):
    """encrypt password"""
    fernet = Fernet(os.environ.get('ENCRYPTION_KEY'))
    return fernet.encrypt(data.encode()).decode()


def decrypt_password(encrypted_data):
    """decrypt password"""
    fernet = Fernet(os.environ.get('ENCRYPTION_KEY'))
    return fernet.decrypt(encrypted_data.encode()).decode()


def create_db_engine(_user, _passw, _db_server = os.environ.get('DATABASE_HOST'),
                                    _db_name = os.environ.get('DATABASE_NAME'),
                                    _db_ms = 'postgresql',):
    """uses sqlalchemy to create the engine"""
    _url = f'{_db_ms}://{_user}:{_passw}@{_db_server}/{_db_name}'
    try:
        _eng = sqla.create_engine(_url)
        with _eng.connect() as _conn:
            _results = _conn.execute(sqla.text(("SELECT 1"))).fetchall()
        return _eng if _results else "SQL-ის გაშვებისას დაფიქსირდა შეცდომა"
    except Exception as e:
        return f"ბაზასთან დაკავშირებისას დაფიქსირდა შეცდომა: {e}"
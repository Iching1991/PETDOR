"""
Gerenciamento de conexão com banco de dados
"""
import sqlite3
from contextlib import contextmanager
import logging
from config import DB_FILE

logger = logging.getLogger(__name__)

@contextmanager
def get_db():
    """Context manager para conexão segura"""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    except Exception as e:
        conn.rollback()
        logger.error(f"Erro no banco: {e}")
        raise
    finally:
        conn.close()

def init_database():
    """Inicializa as tabelas"""
    with get_db() as conn:
        cur = conn.cursor()

        # Tabela de usuários
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha BLOB NOT NULL,
                tipo TEXT NOT NULL,
                data_criacao TEXT NOT NULL,
                ativo INTEGER DEFAULT 1
            )
        """)

        # Tabela de avaliações
        cur.execute("""
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                pet_nome TEXT NOT NULL,
                especie TEXT NOT NULL,
                respostas TEXT NOT NULL,
                pontuacao_total INTEGER NOT NULL,
                pontuacao_maxima INTEGER NOT NULL,
                percentual REAL NOT NULL,
                data_avaliacao TEXT NOT NULL,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)

        # Tabela de reset de senha
        cur.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TEXT NOT NULL,
                used INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        logger.info("Banco de dados inicializado")

# db.py
import sqlite3
from datetime import datetime

DB_FILE = None

def init(db_path):
global DB_FILE
DB_FILE = db_path

def conectar():
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
id INTEGER PRIMARY KEY AUTOINCREMENT,
nome TEXT,
email TEXT UNIQUE,
senha BLOB,
tipo TEXT,
data_criacao TEXT
)
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS avaliacoes (
id INTEGER PRIMARY KEY AUTOINCREMENT,
usuario_id INTEGER,
pet_nome TEXT,
especie TEXT,
respostas TEXT,
pontuacao_total INTEGER,
pontuacao_maxima INTEGER,
percentual REAL,
data_avaliacao TEXT,
FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
)
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS password_resets (
id INTEGER PRIMARY KEY AUTOINCREMENT,
usuario_id INTEGER,
token TEXT,
expires_at TEXT,
used INTEGER DEFAULT 0,
created_at TEXT,
FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
)
""")
conn.commit()
return conn

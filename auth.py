# auth.py
try:
cur.execute("INSERT INTO usuarios (nome, email, senha, tipo, data_criacao) VALUES (?, ?, ?, ?, ?)",
(nome, email, senha_hash, tipo, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
conn.commit()
return True
except Exception:
return False

def authenticate(email, senha):
cur.execute("SELECT id, nome, senha, tipo, data_criacao FROM usuarios WHERE email = ?", (email,))
user = cur.fetchone()
if user and bcrypt.checkpw(senha.encode(), user[2]):
return user
return None

# Token reset (link)
def generate_reset_token(email):
cur.execute("SELECT id, nome FROM usuarios WHERE email = ?", (email,))
u = cur.fetchone()
if not u:
return None
usuario_id = u[0]
token = secrets.token_urlsafe(32)
expires = (datetime.now() + timedelta(hours=TOKEN_EXP_HOURS)).strftime("%Y-%m-%d %H:%M:%S")
cur.execute("INSERT INTO password_resets (usuario_id, token, expires_at, used, created_at) VALUES (?, ?, ?, 0, ?)",
(usuario_id, token, expires, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
conn.commit()
return token

def validate_token(token):
cur.execute("SELECT id, usuario_id, expires_at, used FROM password_resets WHERE token = ? ORDER BY id DESC LIMIT 1", (token,))
row = cur.fetchone()
if not row:
return None, 'Token inválido.'
reset_id, usuario_id, expires_at_str, used = row
expires_at = datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S")
if used:
return None, 'Token já utilizado.'
if datetime.now() > expires_at:
return None, 'Token expirado.'
return {'usuario_id': usuario_id, 'reset_id': reset_id}, None

def reset_password(token, nova_senha):
valid, err = validate_token(token)
if err:
return False, err
usuario_id = valid['usuario_id']
reset_id = valid['reset_id']
nova_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt())
cur.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (nova_hash, usuario_id))
cur.execute("UPDATE password_resets SET used = 1 WHERE id = ?", (reset_id,))
conn.commit()
return True, None

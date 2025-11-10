import streamlit as st
import sqlite3
import bcrypt
from datetime import datetime
from fpdf import FPDF
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pyngrok import ngrok

# ----------------------------
# CONFIGURAÇÕES INICIAIS
# ----------------------------
DB_FILE = "appdor5.db"
APP_NAME = "PET DOR"
EMAIL_USER = st.secrets.get("EMAIL_USER", "")
EMAIL_PASS = st.secrets.get("EMAIL_PASS", "")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

ADS = [
    {"title": "Iranimal", "url": "https://www.iranimal.com.br"},
    {"title": "Vital Pet Care", "url": "https://ccvitalpetcare.com.br"},
    {"title": "Dejodonto", "url": "https://www.dejodonto.com.br"},
    {"title": "Qualivita Pet", "url": "https://petqualivita.com.br"},
    {"title": "Quer apoiar o PET DOR? Envie um email!", "url": f"mailto:{EMAIL_USER}"}
]

# ----------------------------
# BANCO DE DADOS
# ----------------------------
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password_hash TEXT,
    fullname TEXT,
    role TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS pets(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    tutor_id INTEGER,
    vet_id INTEGER,
    FOREIGN KEY (tutor_id) REFERENCES users(id),
    FOREIGN KEY (vet_id) REFERENCES users(id)
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS evaluations(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id INTEGER,
    user_id INTEGER,
    score INTEGER,
    comment TEXT,
    created_at TEXT,
    FOREIGN KEY (pet_id) REFERENCES pets(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")
conn.commit()

# ----------------------------
# FUNÇÕES AUXILIARES
# ----------------------------
def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode("utf-8"), hashed)

def create_user(username, password, fullname="", role="tutor"):
    cur.execute("SELECT id FROM users WHERE username=?", (username,))
    if cur.fetchone():
        return False
    cur.execute("INSERT INTO users(username,password_hash,fullname,role) VALUES(?,?,?,?)",
                (username, hash_password(password), fullname, role))
    conn.commit()
    return True

def generate_pdf(title, content, author="PET DOR"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    content = content.replace("—", "-")
    pdf.multi_cell(0, 8, content)
    pdf.ln(5)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, f"Gerado por: {author} — {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="R")
    return pdf.output(dest="S").encode("utf-8")

def send_email(to_email, subject, body, attachment_bytes=None, filename="relatorio.pdf"):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    if attachment_bytes:
        part = MIMEApplication(attachment_bytes, Name=filename)
        part["Content-Disposition"] = f'attachment; filename="{filename}"'
        msg.attach(part)
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

def start_ngrok(port=8501):
    for t in ngrok.get_tunnels():
        ngrok.disconnect(t.public_url)
    http_tunnel = ngrok.connect(addr=port, bind_tls=True)
    return http_tunnel.public_url

# ----------------------------
# INTERFACE STREAMLIT
# ----------------------------
st.set_page_config(page_title=APP_NAME, layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.role = None

# --- LOGIN ---
if not st.session_state.logged_in:
    st.title(APP_NAME)
    login_col1, login_col2 = st.columns(2)
    with login_col1:
        username = st.text_input("Usuário")
    with login_col2:
        password = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        cur.execute("SELECT id, password_hash, role FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        if row and check_password(password, row[1]):
            st.session_state.logged_in = True
            st.session_state.user_id = row[0]
            st.session_state.username = username
            st.session_state.role = row[2]
        else:
            st.error("Usuário ou senha inválidos")

# --- REGISTRO DE NOVO USUÁRIO ---
st.subheader("Cadastrar novo usuário")
new_user_col1, new_user_col2, new_user_col3 = st.columns([2,2,2])
with new_user_col1:
    new_username = st.text_input("Novo usuário", key="new_user")
with new_user_col2:
    new_password = st.text_input("Nova senha", type="password", key="new_pass")
with new_user_col3:
    new_role = st.selectbox("Tipo", ["tutor","veterinario"])
new_fullname = st.text_input("Nome completo (opcional)", key="new_fullname")
if st.button("Criar usuário"):
    if create_user(new_username, new_password, new_fullname, new_role):
        st.success("Usuário criado com sucesso!")
    else:
        st.error("Usuário já existe")

# --- ANÚNCIOS ---
st.subheader("Anúncios")
for ad in ADS:
    st.markdown(f"[{ad['title']}]({ad['url']})")

# --- CADASTRO DE PETS ---
if st.session_state.logged_in and st.session_state.role=="tutor":
    st.subheader("Cadastrar Pet")
    pet_name = st.text_input("Nome do pet")
    vet_id = st.number_input("ID do veterinário responsável", min_value=1)
    if st.button("Cadastrar pet"):
        cur.execute("INSERT INTO pets(name,tutor_id,vet_id) VALUES(?,?,?)",
                    (pet_name, st.session_state.user_id, vet_id))
        conn.commit()
        st.success("Pet cadastrado com sucesso!")

# --- AVALIAÇÃO ---
if st.session_state.logged_in:
    st.subheader("Avaliação de Dor")
    if st.session_state.role=="tutor":
        cur.execute("SELECT id,name FROM pets WHERE tutor_id=?", (st.session_state.user_id,))
    else:
        cur.execute("SELECT id,name FROM pets WHERE vet_id=?", (st.session_state.user_id,))
    pets = cur.fetchall()
    pet_dict = {p[1]:p[0] for p in pets}
    if pet_dict:
        selected_pet = st.selectbox("Escolha o pet", list(pet_dict.keys()))
        score = st.slider("Nível de dor (0-10)", 0, 10, 0)
        comment = st.text_area("Comentário (opcional)")
        if st.button("Registrar avaliação"):
            cur.execute("INSERT INTO evaluations(pet_id,user_id,score,comment,created_at) VALUES(?,?,?,?,?)",
                        (pet_dict[selected_pet], st.session_state.user_id, score, comment, datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            st.success("Avaliação registrada!")
    else:
        st.info("Nenhum pet disponível para avaliação.")

    # Histórico de avaliações
    st.subheader("Histórico de Avaliações")
    if st.session_state.role=="tutor":
        cur.execute("""SELECT e.id,p.name,u.fullname,e.score,e.comment,e.created_at
                       FROM evaluations e
                       JOIN pets p ON p.id=e.pet_id
                       JOIN users u ON u.id=e.user_id
                       WHERE p.tutor_id=?""",(st.session_state.user_id,))
    else:
        cur.execute("""SELECT e.id,p.name,u.fullname,e.score,e.comment,e.created_at
                       FROM evaluations e
                       JOIN pets p ON p.id=e.pet_id
                       JOIN users u ON u.id=e.user_id
                       WHERE p.vet_id=?""",(st.session_state.user_id,))
    evals = cur.fetchall()
    for e in evals:
        st.write(f"{e[1]} - {e[2]} - Score: {e[3]} - Comentário: {e[4]} - {e[5]}")

    # PDF e envio de email
    if st.button("Gerar PDF e enviar relatório"):
        content = "\n".join([f"{e[1]} - {e[2]} - Score: {e[3]} - Comentário: {e[4]} - {e[5]}" for e in evals])
        pdf_bytes = generate_pdf("Relatório PET DOR", content, st.session_state.username)
        send_email(EMAIL_USER, "Relatório PET DOR", "Segue o relatório de avaliações.", pdf_bytes)
        st.success("Relatório enviado com sucesso!")

# --- NGROK (opcional) ---
if st.button("Iniciar Ngrok"):
    public_url = start_ngrok()
    st.info(f"Ngrok URL: {public_url}")

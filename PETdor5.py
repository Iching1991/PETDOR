import streamlit as st
import sqlite3
import bcrypt
from datetime import datetime
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import os

# =====================================
# CONFIGURAÇÃO STREAMLIT
# =====================================
st.set_page_config(page_title="PET DOR", page_icon="🐾", layout="centered")

# =====================================
# BANCO DE DADOS
# =====================================
DB_FILE = st.secrets["DB_PATH"]

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
    conn.commit()
    return conn

conn = conectar()
cur = conn.cursor()

# =====================================
# FUNÇÃO DE E-MAIL (GoDaddy)
# =====================================
def enviar_email(destinatario, assunto, corpo):
    try:
        msg = MIMEMultipart()
        msg["From"] = st.secrets["EMAIL_USER"]
        msg["To"] = destinatario
        msg["Subject"] = assunto
        msg.attach(MIMEText(corpo, "html"))

        with smtplib.SMTP_SSL(st.secrets["SMTP_SERVER"], st.secrets["SMTP_PORT"]) as server:
            server.login(st.secrets["EMAIL_USER"], st.secrets["EMAIL_PASSWORD"])
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Erro ao enviar e-mail: {e}")
        return False

# =====================================
# CADASTRO E LOGIN
# =====================================
def cadastrar_usuario(nome, email, senha, tipo):
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
    try:
        cur.execute("INSERT INTO usuarios (nome, email, senha, tipo, data_criacao) VALUES (?, ?, ?, ?, ?)",
                    (nome, email, senha_hash, tipo, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        enviar_email(email, "🐾 Bem-vindo ao PET DOR!",
                     f"<h3>Olá {nome}!</h3><p>Seu cadastro no <b>PET DOR</b> foi realizado com sucesso.<br>"
                     "Agora você pode acessar o sistema e realizar avaliações de dor do seu pet com facilidade.</p>")
        st.success("Cadastro realizado e e-mail de confirmação enviado!")
    except sqlite3.IntegrityError:
        st.warning("E-mail já cadastrado!")

def autenticar(email, senha):
    cur.execute("SELECT id, nome, senha, tipo FROM usuarios WHERE email = ?", (email,))
    user = cur.fetchone()
    if user and bcrypt.checkpw(senha.encode(), user[2]):
        return user
    return None

# =====================================
# PERGUNTAS ORIGINAIS (CÃES E GATOS)
# =====================================
perguntas_caes = [
    "Meu cão tem pouca energia",
    "O apetite do meu cão reduziu",
    "Meu cão reluta para levantar",
    "Meu cão gosta de estar perto de mim",
    "Meu cão foi brincalhão",
    "Meu cão mostrou uma quantidade normal de afeto",
    "Meu cão gostou de ser tocado ou acariciado",
    "Meu cão fez as suas atividades favoritas",
    "Meu cão dormiu bem durante a noite",
    "Meu cão agiu normalmente",
    "Meu cão teve problemas para levantar-se ou deitar-se",
    "Meu cão teve problemas para caminhar",
    "Meu cão caiu ou perdeu o equilíbrio",
    "Meu cão comeu normalmente a sua comida favorita",
    "Meu cão teve problemas para ficar confortável"
]

perguntas_gatos = [
    "Meu gato salta para cima",
    "Meu gato salta até a altura do balcão da cozinha ou alturas similares de uma só vez",
    "Meu gato pula para baixo",
    "Meu gato brinca com brinquedos e/ou persegue objetos",
    "Meu gato brinca e interage com outros animais de estimação",
    "Meu gato levanta-se de uma posição de descanso",
    "Meu gato deita-se e/ou senta-se",
    "Meu gato espreguiça-se",
    "Meu gato se limpa normalmente"
]

# =====================================
# AVALIAÇÃO
# =====================================
def realizar_avaliacao(usuario_id):
    st.subheader("🐕‍🦺 Avaliação de Dor")

    pet_nome = st.text_input("Nome do Pet")
    especie = st.selectbox("Espécie", ["Cachorro", "Gato"])
    perguntas = perguntas_caes if especie == "Cachorro" else perguntas_gatos

    respostas = []
    total = 0

    st.info("Avalie de 0 (nunca) a 5 (sempre) o comportamento observado.")

    for p in perguntas:
        r = st.slider(p, 0, 5, 0)
        respostas.append(r)
        total += r

    maximo = len(perguntas) * 5
    percentual = (total / maximo) * 100

    if st.button("Gerar Relatório"):
        cur.execute("""
            INSERT INTO avaliacoes (usuario_id, pet_nome, especie, respostas, pontuacao_total, pontuacao_maxima, percentual, data_avaliacao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (usuario_id, pet_nome, especie, str(respostas), total, maximo, percentual, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

        gerar_relatorio_pdf(pet_nome, especie, percentual)
        st.success("Relatório gerado e salvo com sucesso!")
        st.download_button("Baixar relatório PDF", open(f"relatorio_{pet_nome}.pdf", "rb"), f"relatorio_{pet_nome}.pdf")

# =====================================
# RELATÓRIO PDF
# =====================================
def gerar_relatorio_pdf(pet, especie, percentual):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relatório de Dor - PET DOR", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Nome do Pet: {pet}", ln=True)
    pdf.cell(0, 10, f"Espécie: {especie}", ln=True)
    pdf.cell(0, 10, f"Nível de Dor: {percentual:.1f}%", ln=True)
    pdf.ln(10)

    if percentual < 30:
        texto = "Baixa probabilidade de dor. Continue observando o comportamento."
    elif percentual < 60:
        texto = "Moderada probabilidade de dor. Avalie e monitore nos próximos dias."
    else:
        texto = "Alta probabilidade de dor. Recomenda-se avaliação veterinária imediata."
    pdf.multi_cell(0, 10, texto)

    pdf.output(f"relatorio_{pet}.pdf")

# =====================================
# INTERFACE
# =====================================
st.title("🐾 PET DOR")
st.write("Sistema de Avaliação de Dor Animal")

menu = st.sidebar.selectbox("Menu", ["Login", "Cadastrar", "Sobre"])

if menu == "Cadastrar":
    nome = st.text_input("Nome completo")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    tipo = st.selectbox("Tipo de usuário", ["Tutor", "Veterinário", "Clínica"])
    if st.button("Cadastrar"):
        cadastrar_usuario(nome, email, senha, tipo)

elif menu == "Login":
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        user = autenticar(email, senha)
        if user:
            st.success(f"Bem-vindo, {user[1]}!")
            realizar_avaliacao(user[0])
        else:
            st.error("E-mail ou senha incorretos.")

elif menu == "Sobre":
    st.markdown("""
    ### 🩺 Sobre o PET DOR
    O **PET DOR** é uma ferramenta gratuita que auxilia tutores e veterinários
    a identificarem sinais de dor em cães e gatos, com base em comportamento e rotina.

    Desenvolvido com base em questionários clínicos adaptados (CBPI e FMPI),
    o sistema fornece uma estimativa percentual da presença de dor.
    """)

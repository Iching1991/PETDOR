# app_petdor.py
import streamlit as st
import sqlite3
import bcrypt
from datetime import datetime
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import urllib.parse
import pandas as pd

# ---------------------------
# Config Page & SVG Waves
# ---------------------------
st.set_page_config(page_title="PET DOR", layout="wide", page_icon="🐾")

# SVG ondulante no topo (gradiente azul-claro -> verde-claro)
svg_waves = """
<div style="position:relative; overflow:hidden;">
  <svg viewBox="0 0 1200 200" preserveAspectRatio="none" style="width:100%; height:130px;">
    <defs>
      <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#e6f4ff"/>
        <stop offset="50%" stop-color="#dff8ef"/>
        <stop offset="100%" stop-color="#ffffff"/>
      </linearGradient>
    </defs>
    <path d="M0,100 C300,200 900,0 1200,100 L1200,00 L0,0 Z" fill="url(#g1)">
      <animate attributeName="d" dur="6s" repeatCount="indefinite"
        values="
          M0,100 C300,200 900,0 1200,100 L1200,00 L0,0 Z;
          M0,100 C300,0 900,200 1200,100 L1200,00 L0,0 Z;
          M0,100 C200,180 1000,20 1200,100 L1200,00 L0,0 Z;
          M0,100 C300,200 900,0 1200,100 L1200,00 L0,0 Z
        " />
    </path>
  </svg>
</div>
"""
st.markdown(svg_waves, unsafe_allow_html=True)

# Top header with generic logo (texto estilizado)
st.markdown("""
    <div style="display:flex; align-items:center; gap:16px; margin-top:-60px;">
      <div style="width:86px;height:86px;border-radius:18px;background:linear-gradient(135deg,#7cc8ff,#a6f0d4);display:flex;align-items:center;justify-content:center;box-shadow:0 6px 18px rgba(0,0,0,0.08);">
        <div style="font-weight:900;color:#fff;font-size:28px;">PD</div>
      </div>
      <div>
        <h1 style="margin:0; color:#0B5FFF;">PET DOR</h1>
        <div style="color:#2F9E44; font-weight:600;">Avaliação de dor em pets — prático e integrado</div>
      </div>
    </div>
""", unsafe_allow_html=True)

st.write("")  # spacer

# ---------------------------
# Database (SQLite)
# ---------------------------
DB_FILE = "petdor.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT,
    nome TEXT,
    email TEXT,
    senha_hash BLOB,
    crmv TEXT,
    clinic_id INTEGER
)
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS clinicas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    email TEXT,
    endereco TEXT
)
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS avaliacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tutor_id INTEGER,
    pet_nome TEXT,
    especie TEXT,
    raw_score REAL,
    max_score REAL,
    percent REAL,
    vet_email TEXT,
    comentario TEXT,
    created_at TEXT
)
""")
conn.commit()

# ---------------------------
# Perguntas originais (Cães e Gatos)
# ---------------------------
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

# ---------------------------
# Utilitários: hash, check senha, calculo percentual, salvar
# ---------------------------
def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

def check_password(password: str, senha_hash: bytes) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), senha_hash)
    except:
        return False

def calcular_percentual(respostas: list, escala_max: int) -> float:
    soma = sum(respostas)
    max_total = len(respostas) * escala_max
    if max_total == 0:
        return 0.0
    percentual = (soma / max_total) * 100.0
    return round(percentual, 1)

def gerar_pdf_relatorio(tutor_nome, pet_nome, especie, percentual, respostas_summary, comentario):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relatório PET DOR", ln=True, align="C")
    pdf.ln(6)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Tutor: {tutor_nome}", ln=True)
    pdf.cell(0, 8, f"Pet: {pet_nome} ({especie})", ln=True)
    pdf.cell(0, 8, f"Resultado: {percentual} % de dor", ln=True)
    pdf.ln(4)
    pdf.multi_cell(0, 8, "Resumo das respostas:")
    pdf.ln(2)
    for line in respostas_summary:
        pdf.multi_cell(0, 7, "- " + line)
    pdf.ln(6)
    if comentario:
        pdf.multi_cell(0, 7, "Comentário do tutor:")
        pdf.multi_cell(0, 7, comentario)
    pdf.set_font("Arial", "I", 10)
    pdf.ln(6)
    pdf.cell(0, 7, f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="R")
    return pdf.output(dest="S").encode("latin-1", "replace")

def criar_usuario(role, nome, email, senha, crmv=None, clinic_id=None):
    senha_hash = hash_password(senha) if senha else None
    cur.execute("INSERT INTO usuarios (role,nome,email,senha_hash,crmv,clinic_id) VALUES (?,?,?,?,?,?)",
                (role, nome, email, senha_hash, crmv, clinic_id))
    conn.commit()
    return cur.lastrowid

def autenticar_usuario(email, senha):
    cur.execute("SELECT id,role,nome,email,senha_hash,crmv,clinic_id FROM usuarios WHERE email=?", (email,))
    row = cur.fetchone()
    if not row:
        return None
    user_id, role, nome, email_db, senha_hash, crmv, clinic_id = row
    if senha_hash is None:
        return None
    if check_password(senha, senha_hash):
        return {"id": user_id, "role": role, "nome": nome, "email": email_db, "crmv": crmv, "clinic_id": clinic_id}
    return None

def criar_clinica(nome, email=None, endereco=None):
    cur.execute("INSERT INTO clinicas (nome,email,endereco) VALUES (?,?,?)", (nome, email, endereco))
    conn.commit()
    return cur.lastrowid

def listar_clinicas():
    cur.execute("SELECT id,nome FROM clinicas")
    return cur.fetchall()

def salvar_avaliacao(tutor_id, pet_nome, especie, raw_score, max_score, percent, vet_email, comentario):
    cur.execute("""INSERT INTO avaliacoes
                   (tutor_id, pet_nome, especie, raw_score, max_score, percent, vet_email, comentario, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (tutor_id, pet_nome, especie, raw_score, max_score, percent, vet_email, comentario, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    return cur.lastrowid

def buscar_avaliacoes_por_vet(vet_email):
    cur.execute("SELECT * FROM avaliacoes WHERE vet_email=?", (vet_email,))
    return cur.fetchall()

def buscar_avaliacoes_por_tutor(tutor_id):
    cur.execute("SELECT * FROM avaliacoes WHERE tutor_id=?", (tutor_id,))
    return cur.fetchall()

# ---------------------------
# Envio real por SMTP (GoDaddy)
# ---------------------------
def enviar_relatorio_email_real(tutor_nome, tutor_email, pet_nome, especie, percentual, vet_email, pdf_bytes):
    remetente = "relatorio@petdor.app"
    try:
        senha = st.secrets["EMAIL_PASSWORD"]
    except Exception as e:
        st.error("Senha de e-mail não encontrada em .streamlit/secrets.toml (EMAIL_PASSWORD).")
        return ["❌ Configuração de e-mail ausente"]

    servidor_smtp = "smtp.secureserver.net"
    porta = 465  # SSL

    destinatarios = ["relatorio@petdor.app"]  # backup
    if tutor_email:
        destinatarios.append(tutor_email)
    if vet_email:
        destinatarios.append(vet_email)

    assunto = f"Relatório PET DOR - {pet_nome} ({especie})"
    corpo = f"Olá,\n\nSegue em anexo o relatório de avaliação de dor do pet {pet_nome} ({especie}).\nPercentual de dor: {percentual}%\n\nTutor: {tutor_nome}\nE-mail do tutor: {tutor_email or 'não informado'}\n\nAtenciosamente,\nEquipe PET DOR"

    try:
        msg = MIMEMultipart()
        msg["From"] = remetente
        msg["To"] = ", ".join(destinatarios)
        msg["Subject"] = assunto
        msg.attach(MIMEText(corpo, "plain"))

        anexado = MIMEApplication(pdf_bytes, _subtype="pdf")
        anexado.add_header("Content-Disposition", "attachment", filename=f"relatorio_{pet_nome}.pdf")
        msg.attach(anexado)

        with smtplib.SMTP_SSL(servidor_smtp, porta) as server:
            server.login(remetente, senha)
            server.send_message(msg)

        # Return success messages list
        msgs = [f"✅ Relatório enviado para: {', '.join(destinatarios)}"]
        return msgs
    except Exception as e:
        return [f"❌ Erro ao enviar e-mail: {str(e)}"]

# ---------------------------
# Sessão e logs
# ---------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "user" not in st.session_state:
    st.session_state.user = None
if "eval_info" not in st.session_state:
    st.session_state.eval_info = None
if "logs_envios" not in st.session_state:
    st.session_state.logs_envios = []

# Banner de parceiros (simples) no lado direito
banners = [
    {"nome": "Iranimal", "url": "https://www.iranimal.com.br", "imagem": "https://via.placeholder.com/300x120?text=Iranimal"},
    {"nome": "Vital Pet Care", "url": "https://ccvitalpetcare.com.br", "imagem": "https://via.placeholder.com/300x120?text=Vital+Pet+Care"},
]

# ---------------------------
# UI: Tela inicial - login e cadastro (com e-mail obrigatório)
# ---------------------------
def tela_inicial():
    st.markdown("<div style='padding:12px; border-radius:12px; background:#fff; box-shadow:0 6px 20px rgba(0,0,0,0.04);'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:#0B5FFF;'>Entrar ou Cadastrar</h2>", unsafe_allow_html=True)
    col_main, col_right = st.columns([3,1])

    with col_right:
        st.markdown("### Parceiros")
        for b in banners:
            st.image(b["imagem"], use_column_width=True)
            st.markdown(f"[{b['nome']}]({b['url']})", unsafe_allow_html=True)

    with col_main:
        action = st.radio("Escolha:", ["Entrar", "Cadastrar"], index=0, horizontal=True)
        if action == "Entrar":
            st.subheader("Login")
            email = st.text_input("E-mail", key="login_email")
            senha = st.text_input("Senha", type="password", key="login_pass")
            if st.button("Entrar"):
                user = autenticar_usuario(email.strip(), senha)
                if user:
                    st.success(f"Bem vindo(a), {user['nome']} ({user['role']})")
                    st.session_state.user = user
                    if user['role'] == "tutor":
                        st.session_state.page = "avaliacao_iniciar"
                    elif user['role'] == "veterinario":
                        st.session_state.page = "vet_dashboard"
                    elif user['role'] == "clinica":
                        st.session_state.page = "clinica_dashboard"
                    st.experimental_rerun()
                else:
                    st.error("Login inválido. Verifique e-mail/senha.")
        else:
            st.subheader("Cadastro")
            tipo = st.selectbox("Sou:", ["Tutor", "Veterinário", "Clínica"])
            if tipo == "Tutor":
                nome = st.text_input("Nome completo", key="cad_tutor_nome")
                email = st.text_input("E-mail (obrigatório)", key="cad_tutor_email")
                pet_nome = st.text_input("Nome do pet", key="cad_pet_nome")
                especie = st.selectbox("Espécie", ["Cão", "Gato", "Coelho","Aves","Répteis","Porquinho-da-índia"], key="cad_pet_especie")
                senha = st.text_input("Senha (crie uma)", type="password", key="cad_tutor_senha")
                if st.button("Cadastrar Tutor"):
                    if not nome or not pet_nome or not senha or not email:
                        st.warning("Preencha pelo menos: nome, e-mail, nome do pet e senha.")
                    else:
                        user_id = criar_usuario("tutor", nome, email.strip(), senha)
                        st.success("Tutor cadastrado com sucesso! Faça login para iniciar avaliação.")
            elif tipo == "Veterinário":
                nome = st.text_input("Nome completo", key="cad_vet_nome")
                email = st.text_input("E-mail (obrigatório)", key="cad_vet_email")
                crmv = st.text_input("CRMV (registro profissional)", key="cad_vet_crmv")
                st.markdown("Associação com clínica (opcional)")
                clinics = listar_clinicas()
                clinic_select = None
                if clinics:
                    clinic_options = {f"{c[1]} (id:{c[0]})": c[0] for c in clinics}
                    clinic_sel = st.selectbox("Escolher clínica existente", list(clinic_options.keys()))
                    clinic_select = clinic_options[clinic_sel]
                if st.checkbox("Cadastrar nova clínica"):
                    new_clinic_name = st.text_input("Nome da clínica", key="new_clinic_name")
                    new_clinic_email = st.text_input("E-mail da clínica (opcional)", key="new_clinic_email")
                    new_clinic_address = st.text_input("Endereço (opcional)", key="new_clinic_address")
                    if st.button("Salvar clínica"):
                        if not new_clinic_name:
                            st.warning("Informe o nome da clínica.")
                        else:
                            clinic_id = criar_clinica(new_clinic_name, new_clinic_email, new_clinic_address)
                            st.success("Clínica criada com sucesso.")
                            clinic_select = clinic_id
                senha = st.text_input("Senha (crie uma)", type="password", key="cad_vet_senha")
                if st.button("Cadastrar Veterinário"):
                    if not nome or not senha or not email:
                        st.warning("Preencha pelo menos: nome, e-mail e senha.")
                    else:
                        user_id = criar_usuario("veterinario", nome, email.strip(), senha, crmv, clinic_select)
                        st.success("Veterinário cadastrado com sucesso! Faça login para acessar o painel.")
            else:  # Clinica
                nome = st.text_input("Nome da clínica", key="cad_clin_nome")
                email = st.text_input("E-mail (obrigatório)", key="cad_clin_email")
                endereco = st.text_input("Endereço (opcional)", key="cad_clin_end")
                senha = st.text_input("Senha (crie uma)", type="password", key="cad_clin_senha")
                if st.button("Cadastrar Clínica"):
                    if not nome or not senha or not email:
                        st.warning("Preencha pelo menos: nome, e-mail e senha.")
                    else:
                        clinic_id = criar_clinica(nome, email.strip(), endereco)
                        user_id = criar_usuario("clinica", nome, email.strip(), senha, None, clinic_id)
                        st.success("Clínica cadastrada com sucesso! Faça login para acessar o painel.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Tela iniciar avaliação (tutor)
# ---------------------------
def tela_iniciar_avaliacao():
    st.markdown("<div style='padding:16px; background:#fff; border-radius:12px; box-shadow:0 6px 20px rgba(0,0,0,0.04)'>", unsafe_allow_html=True)
    st.header("Iniciar Avaliação")
    user = st.session_state.get("user")
    if not user:
        st.warning("Usuário não autenticado.")
        st.session_state.page = "home"
        st.experimental_rerun()
        return

    st.subheader("Dados do Tutor / Pet")
    col1, col2 = st.columns(2)
    with col1:
        tutor_nome = st.text_input("Nome do tutor", value=user.get("nome",""), key="tutor_nome")
        tutor_email = st.text_input("E-mail do tutor (obrigatório)", value=user.get("email","") or "", key="tutor_email")
    with col2:
        pet_nome = st.text_input("Nome do pet", key="pet_nome")
        especie = st.selectbox("Espécie", ["Cão","Gato","Coelho","Aves","Répteis","Porquinho-da-índia"], key="pet_especie")
        vet_email = st.text_input("E-mail do veterinário (opcional)", key="vet_email")

    if st.button("Começar Avaliação"):
        if not tutor_nome or not pet_nome or not tutor_email:
            st.warning("Preencha pelo menos o nome do tutor, e-mail e do pet.")
        else:
            st.session_state.eval_info = {
                "tutor_id": user["id"],
                "tutor_nome": tutor_nome,
                "tutor_email": tutor_email,
                "pet_nome": pet_nome,
                "especie": especie,
                "vet_email": vet_email
            }
            st.session_state.page = "avaliacao"
            st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Tela de avaliação (com perguntas originais)
# ---------------------------
def tela_avaliacao():
    st.markdown("<div style='padding:16px; background:#fff; border-radius:12px; box-shadow:0 6px 20px rgba(0,0,0,0.04)'>", unsafe_allow_html=True)
    st.header("Avaliação de Dor")
    info = st.session_state.get("eval_info")
    if not info:
        st.warning("Nenhuma avaliação iniciada. Volte e preencha os dados do tutor/pet.")
        if st.button("Voltar"):
            st.session_state.page = "avaliacao_iniciar"
            st.experimental_rerun()
        return

    st.markdown(f"**Tutor:** {info['tutor_nome']}  &nbsp;   **Pet:** {info['pet_nome']}  &nbsp;   **Espécie:** {info['especie']}")
    especie = info['especie']

    respostas = []
    respostas_summary = []
    comentario = st.text_area("Comentário (opcional)")

    if especie == "Cão":
        escala_max = 7
        st.write("Use os sliders (0 = normal / 7 = alteração grave).")
        for i, pergunta in enumerate(perguntas_caes):
            key = f"cao_{i}"
            valor = st.slider(pergunta + f" ({0}–{escala_max})", 0, escala_max, 0, key=key)
            respostas.append(valor)
            respostas_summary.append(f"{pergunta} — {valor}/{escala_max}")
    elif especie == "Gato":
        escala_max = 4
        st.write("Use os sliders (0 = normal / 4 = alteração grave).")
        for i, pergunta in enumerate(perguntas_gatos):
            key = f"gato_{i}"
            valor = st.slider(pergunta + f" ({0}–{escala_max})", 0, escala_max, 0, key=key)
            respostas.append(valor)
            respostas_summary.append(f"{pergunta} — {valor}/{escala_max}")
    else:
        st.info("🔧 Em construção — questionário específico para esta espécie ainda será desenvolvido.")
        escala_max = 1
        # apenas pergunta genérica para registro mínimo
        gen = st.selectbox("O animal demonstra sinais visíveis de dor?", ["Não", "Sim"], key="outro_gen")
        respostas = [1 if gen=="Sim" else 0]
        respostas_summary.append(f"Sinais visíveis de dor: {gen}")

    if st.button("Enviar Avaliação"):
        percentual = calcular_percentual(respostas, escala_max)
        raw_score = sum(respostas)
        max_score = len(respostas) * escala_max

        # salvar no banco
        aval_id = salvar_avaliacao(info['tutor_id'], info['pet_nome'], info['especie'], raw_score, max_score, percentual, info.get('vet_email'), comentario)

        # gerar pdf
        pdf_bytes = gerar_pdf_relatorio(info['tutor_nome'], info['pet_nome'], info['especie'], percentual, respostas_summary, comentario)

        # enviar por e-mail (real)
        mensagens = enviar_relatorio_email_real(info['tutor_nome'], info.get('tutor_email'), info['pet_nome'], info['especie'], percentual, info.get('vet_email'), pdf_bytes)

        # apresentar resultado
        st.markdown(f"### Resultado: **{percentual}%**")
        if percentual >= 70:
            st.error("🚨 Dor intensa detectada! Procure um veterinário imediatamente.")
        elif percentual >= 40:
            st.warning("⚠️ Dor moderada detectada. Recomendamos consulta veterinária.")
        else:
            st.success("✅ Sem dor significativa detectada no momento.")

        # mostrar mensagens de envio
        for m in mensagens:
            st.info(m)

        # download do PDF
        st.download_button("📥 Baixar relatório (PDF)", data=pdf_bytes, file_name=f"relatorio_{info['pet_nome']}.pdf", mime="application/pdf")

        # links de compartilhamento
        texto = f"Relatório PET DOR - Pet: {info['pet_nome']} ({info['especie']}) - Dor: {percentual}%"
        texto_enc = urllib.parse.quote(texto)
        wa_link = f"https://wa.me/?text={texto_enc}"
        tg_link = f"https://t.me/share/url?url=&text={texto_enc}"
        sms_link = f"sms:?&body={texto_enc}"
        st.markdown(f"[📱 WhatsApp]({wa_link})  &nbsp; [💬 Telegram]({tg_link})  &nbsp; [📩 SMS]({sms_link})", unsafe_allow_html=True)

        # log local de envios para administração
        st.session_state.logs_envios.append({
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "pet": info['pet_nome'],
            "tutor": info['tutor_nome'],
            "tutor_email": info.get('tutor_email'),
            "vet_email": info.get('vet_email') or "-",
            "percentual": percentual,
            "status": "Enviado (ver mensagens acima)"
        })

        # limpar sessão de avaliação para evitar reenvio acidental
        st.session_state.eval_info = None

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Tela Veterinário e Clinica
# ---------------------------
def tela_vet_dashboard():
    st.markdown("<div style='padding:16px; background:#fff; border-radius:12px; box-shadow:0 6px 20px rgba(0,0,0,0.04)'>", unsafe_allow_html=True)
    st.header("Painel do Veterinário")
    user = st.session_state.get("user")
    if not user:
        st.warning("Usuário não autenticado.")
        st.session_state.page = "home"
        st.experimental_rerun()
        return
    st.subheader(f"Bem-vindo, {user['nome']}")
    rows = buscar_avaliacoes_por_vet(user.get("email"))
    if not rows:
        st.info("Nenhuma avaliação encontrada para o seu e-mail.")
    else:
        for r in rows:
            _, tutor_id, pet_nome, especie, raw_score, max_score, percent, vet_email, comentario, created_at = r
            st.markdown(f"**{pet_nome}** ({especie}) — {percent}% — {created_at}")
            if comentario:
                st.markdown(f"_Comentário:_ {comentario}")
    st.markdown("</div>", unsafe_allow_html=True)

def tela_clinica_dashboard():
    st.markdown("<div style='padding:16px; background:#fff; border-radius:12px; box-shadow:0 6px 20px rgba(0,0,0,0.04)'>", unsafe_allow_html=True)
    st.header("Painel da Clínica")
    user = st.session_state.get("user")
    if not user:
        st.warning("Usuário não autenticado.")
        st.session_state.page = "home"
        st.experimental_rerun()
        return
    st.subheader(f"Clínica: {user.get('nome')}")
    st.write("Funcionalidades futuras: ver veterinários, pacientes e relatórios.")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Administração (logs export)
# ---------------------------
def tela_admin():
    st.markdown("<div style='padding:16px; background:#fff; border-radius:12px; box-shadow:0 6px 20px rgba(0,0,0,0.04)'>", unsafe_allow_html=True)
    st.header("📊 Administração - Logs de Envios")
    logs = st.session_state.get("logs_envios", [])
    if not logs:
        st.info("Nenhum relatório enviado nesta sessão.")
    else:
        df = pd.DataFrame(logs)
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar Log de Envios (CSV)", csv, "logs_envios_petdor.csv", "text/csv")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Routing top-level
# ---------------------------
page = st.session_state.page

if page == "home":
    tela_inicial()
elif page == "avaliacao_iniciar":
    if st.session_state.user and st.session_state.user.get("role") == "tutor":
        tela_iniciar_avaliacao()
    else:
        st.warning("Apenas tutores autenticados podem iniciar avaliação.")
        if st.button("Voltar para início"):
            st.session_state.page = "home"
            st.experimental_rerun()
elif page == "avaliacao":
    tela_avaliacao()
elif page == "vet_dashboard":
    tela_vet_dashboard()
elif page == "clinica_dashboard":
    tela_clinica_dashboard()
elif page == "admin":
    tela_admin()
elif page == "vet_dashboard":
    tela_vet_dashboard()
elif page == "clinica_dashboard":
    tela_clinica_dashboard()
else:
    tela_inicial()
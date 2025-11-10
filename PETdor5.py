# PETdor.py
import streamlit as st
import sqlite3
import bcrypt
from datetime import datetime
from fpdf import FPDF
import time
import threading
import urllib.parse

# ---------------------------
# Configuração de página / tema
# ---------------------------
st.set_page_config(page_title="PET DOR", layout="wide", page_icon="🐾")
# CSS custom (cores claras azul/verde)
st.markdown(
    """
    <style>
    .main-title {font-size:32px; color:#0B5FFF; font-weight:700;}
    .sub {color:#2F9E44;}
    .card {background: #ffffff; border-radius:12px; padding:16px; box-shadow: 0 4px 10px rgba(0,0,0,0.06);}
    .right-panel {position: sticky; top: 20px;}
    .small-muted {color: #6b7280; font-size:12px;}
    .btn-primary {background-color:#0B5FFF; color:white;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Banco de dados SQLite (local)
# ---------------------------
DB_FILE = "petdor.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cur = conn.cursor()

# Usuários: role in ['tutor','veterinario','clinica']
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

# Clinicas
cur.execute("""
CREATE TABLE IF NOT EXISTS clinicas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    email TEXT,
    endereco TEXT
)
""")

# Avaliacoes
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
# BANNERS (parceiros) - placeholders de imagem
# ---------------------------
banners = [
    {"nome": "Iranimal", "url": "https://www.iranimal.com.br", "imagem": "https://via.placeholder.com/300x120?text=Iranimal"},
    {"nome": "Vital Pet Care", "url": "https://ccvitalpetcare.com.br", "imagem": "https://via.placeholder.com/300x120?text=Vital+Pet+Care"},
    {"nome": "Dejodonto", "url": "https://www.dejodonto.com.br", "imagem": "https://via.placeholder.com/300x120?text=Dejodonto"},
    {"nome": "Qualivita Pet", "url": "https://petqualivita.com.br", "imagem": "https://via.placeholder.com/300x120?text=Qualivita+Pet"},
]

# ---------------------------
# Perguntas por espécie
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
# Funções utilitárias
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

def enviar_relatorio_simulado(tutor_nome, tutor_email, pet_nome, especie, percentual, vet_email, pdf_bytes):
    """
    Simulação de envio de relatório.
    Está pronta para substituir por implementação SMTP real futuramente.
    Atualmente registra que o relatório foi 'enviado' e retorna mensagem.
    """
    # Registrar no banco: (já salvamos a avaliação em avaliacoes table)
    # Simular envio para relatorio@petdor.app e, se presente, para vet_email
    mensagens = [f"Relatório enviado para relatorio@petdor.app"]
    if vet_email:
        mensagens.append(f"Relatório enviado também para {vet_email}")
    # Se tutor tem email, podemos indicar que foi enviado para ele também (opcional)
    if tutor_email:
        mensagens.append(f"Cópia enviada para tutor: {tutor_email}")
    # retornar mensagens (não realiza SMTP ainda)
    return mensagens

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
# Thread dos banners (direita)
# ---------------------------

def start_banner_thread(banners, placeholder):
    def loop_banners():
        while True:
            for b in banners:
                with placeholder.container():
                    st.image(b["imagem"], use_column_width=True)
                    st.markdown(f"<div style='text-align:center; padding-top:6px;'><a target='_blank' href='{b['url']}'>{b['nome']}</a></div>", unsafe_allow_html=True)
                time.sleep(5)
    thread = threading.Thread(target=loop_banners, daemon=True)
    thread.start()

# ---------------------------
# UI: Tela inicial (boas-vindas) com login e cadastro
# ---------------------------

def tela_inicial():
    st.markdown("<div class='main-title'>PET DOR</div>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Avaliação simples da dor em pets — rápido, prático e preparado para integração com clínicas e aplicativos.</div>", unsafe_allow_html=True)
    st.write("")
    # Layout: main area + right banner column
    col_main, col_right = st.columns([3, 1])
    with col_right:
        st.markdown("<div class='card right-panel'>", unsafe_allow_html=True)
        banner_placeholder = st.empty()
        start_banner_thread(banners, banner_placeholder)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_main:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Entrar ou cadastrar")
        action = st.radio("Escolha:", ["Entrar", "Cadastrar"], index=0, horizontal=True)
        st.write("")
        if action == "Entrar":
            st.markdown("#### Login")
            email = st.text_input("E-mail", key="login_email")
            senha = st.text_input("Senha", type="password", key="login_pass")
            if st.button("Entrar"):
                user = autenticar_usuario(email.strip(), senha)
                if user:
                    st.success(f"Bem vindo(a), {user['nome']} ({user['role']})")
                    st.session_state.user = user
                    # redireciona conforme role
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
            st.markdown("#### Cadastro")
            tipo = st.selectbox("Sou:", ["Tutor", "Veterinário", "Clínica"])
            if tipo == "Tutor":
                nome = st.text_input("Nome completo", key="cad_tutor_nome")
                email = st.text_input("E-mail (opcional)", key="cad_tutor_email")
                pet_nome = st.text_input("Nome do pet", key="cad_pet_nome")
                especie = st.selectbox("Espécie", ["Cão", "Gato"], key="cad_pet_especie")
                idade = st.text_input("Idade (opcional)", key="cad_pet_idade")
                senha = st.text_input("Senha (crie uma)", type="password", key="cad_tutor_senha")
                if st.button("Cadastrar Tutor"):
                    if not nome or not pet_nome or not senha:
                        st.warning("Preencha pelo menos: nome, nome do pet e senha.")
                    else:
                        user_id = criar_usuario("tutor", nome, email.strip() if email else None, senha)
                        st.success("Tutor cadastrado com sucesso! Faça login para iniciar avaliação.")
            elif tipo == "Veterinário":
                nome = st.text_input("Nome completo", key="cad_vet_nome")
                email = st.text_input("E-mail (opcional)", key="cad_vet_email")
                crmv = st.text_input("CRMV (registro profissional)", key="cad_vet_crmv")
                # selecionar clinica existente ou criar nova
                st.markdown("Associação com clínica (opcional)")
                clinics = listar_clinicas()
                clinic_options = {f"{c[1]} (id:{c[0]})": c[0] for c in clinics}
                clinic_select = None
                if clinics:
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
                    if not nome or not senha:
                        st.warning("Preencha pelo menos: nome e senha.")
                    else:
                        user_id = criar_usuario("veterinario", nome, email.strip() if email else None, senha, crmv, clinic_select)
                        st.success("Veterinário cadastrado com sucesso! Faça login para acessar o painel.")
            else:  # Clinica
                nome = st.text_input("Nome da clínica", key="cad_clin_nome")
                email = st.text_input("E-mail (opcional)", key="cad_clin_email")
                endereco = st.text_input("Endereço (opcional)", key="cad_clin_end")
                senha = st.text_input("Senha (crie uma)", type="password", key="cad_clin_senha")
                if st.button("Cadastrar Clínica"):
                    if not nome or not senha:
                        st.warning("Preencha pelo menos: nome e senha.")
                    else:
                        clinic_id = criar_clinica(nome, email.strip() if email else None, endereco)
                        # criar usuario 'clinica' vinculado a clinic_id
                        user_id = criar_usuario("clinica", nome, email.strip() if email else None, senha, None, clinic_id)
                        st.success("Clínica cadastrada com sucesso! Faça login para acessar o painel.")
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Página: iniciar avaliação (após login tutor)
# ---------------------------
def tela_iniciar_avaliacao():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header("Iniciar Avaliação")
    user = st.session_state.get("user")
    if not user:
        st.warning("Usuário não autenticado.")
        st.session_state.page = "home"
        st.experimental_rerun()
        return

    # Pedir confirmação dos dados do tutor/pet (permitir editar)
    st.subheader("Dados do Tutor / Pet")
    col1, col2 = st.columns(2)
    with col1:
        tutor_nome = st.text_input("Nome do tutor", value=user.get("nome", ""), key="tutor_nome")
        tutor_email = st.text_input("E-mail do tutor (opcional)", value=user.get("email", "") or "", key="tutor_email")
    with col2:
        pet_nome = st.text_input("Nome do pet", key="pet_nome")
        especie = st.selectbox("Espécie", ["Cão", "Gato"], key="pet_especie")
        # opcional: nome ou e-mail do veterinário
        vet_email = st.text_input("E-mail do veterinário (opcional)", key="vet_email")

    if st.button("Começar Avaliação"):
        if not tutor_nome or not pet_nome:
            st.warning("Preencha pelo menos o nome do tutor e do pet.")
        else:
            # salvamos temporariamente os dados na sessão
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
# Página: Avaliação
# ---------------------------
def tela_avaliacao():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header("Avaliação de Dor")
    info = st.session_state.get("eval_info")
    if not info:
        st.warning("Nenhuma avaliação iniciada. Volte e preencha os dados do tutor/pet.")
        if st.button("Voltar"):
            st.session_state.page = "avaliacao_iniciar"
            st.experimental_rerun()
        return

    st.markdown(f"**Tutor:** {info['tutor_nome']}  &nbsp;   **Pet:** {info['pet_nome']}  &nbsp;   **Espécie:** {info['especie']}")
    st.write("Use os sliders para avaliar cada item (0 = normal, 7 ou 4 = alteração grave).")

    respostas = []
    perguntas = perguntas_caes if info['especie'] == "Cão" else perguntas_gatos
    escala_max = 7 if info['especie'] == "Cão" else 4

    # Para manter os sliders entre reruns, usar keys baseados em index
    for i, pergunta in enumerate(perguntas):
        key = f"p_{i}"
        default = 0
        valor = st.slider(pergunta, 0, escala_max, default, key=key)
        respostas.append(valor)

    comentario = st.text_area("Comentário (opcional)")

    if st.button("Enviar Avaliação"):
        percentual = calcular_percentual(respostas, escala_max)
        raw_score = sum(respostas)
        max_score = len(respostas) * escala_max

        # salvar no banco
        aval_id = salvar_avaliacao(info['tutor_id'], info['pet_nome'], info['especie'], raw_score, max_score, percentual, info.get('vet_email'), comentario)

        # gerar pdf
        summary_lines = []
        for q, r in zip(perguntas, respostas):
            summary_lines.append(f"{q} — {r}/{escala_max}")

        pdf_bytes = gerar_pdf_relatorio(info['tutor_nome'], info['pet_nome'], info['especie'], percentual, summary_lines, comentario)

        # simular envio de relatório
        mensagens = enviar_relatorio_simulado(info['tutor_nome'], info.get('tutor_email'), info['pet_nome'], info['especie'], percentual, info.get('vet_email'), pdf_bytes)

        # mostrar resultado com classificação e ações
        st.markdown(f"### Resultado: **{percentual}%**")
        if percentual >= 70:
            st.error("🚨 Dor intensa detectada! Procure um veterinário imediatamente.")
        elif percentual >= 40:
            st.warning("⚠️ Dor moderada detectada. Recomendamos consulta veterinária.")
        else:
            st.success("✅ Sem dor significativa detectada no momento.")

        # mostrar mensagens de 'envio'
        for m in mensagens:
            st.info(m)

        # permitir download do PDF
        st.download_button("📥 Baixar relatório (PDF)", data=pdf_bytes, file_name=f"relatorio_{info['pet_nome']}.pdf", mime="application/pdf")

        # gerar links de compartilhamento (WhatsApp, Telegram, SMS)
        texto = f"Relatório PET DOR - Pet: {info['pet_nome']} ({info['especie']}) - Dor: {percentual}% - Acesse o relatório após o download."
        texto_enc = urllib.parse.quote(texto)
        wa_link = f"https://wa.me/?text={texto_enc}"
        tg_link = f"https://t.me/share/url?url=&text={texto_enc}"
        sms_link = f"sms:?&body={texto_enc}"

        st.markdown("### Compartilhar resultado")
        st.markdown(f"[📱 Enviar por WhatsApp]({wa_link})  &nbsp;  [💬 Enviar por Telegram]({tg_link})  &nbsp;  [📩 Enviar por SMS]({sms_link})", unsafe_allow_html=True)

        # limpar sessão de avaliação para evitar reenvio acidental
        st.session_state.eval_info = None

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------
# Página: Veterinário (painel) - mostra avaliações associadas ao e-mail do vet
# ---------------------------
def tela_vet_dashboard():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header("Painel do Veterinário")
    user = st.session_state.get("user")
    if not user:
        st.warning("Usuário não autenticado.")
        st.session_state.page = "home"
        st.experimental_rerun()
        return
    st.subheader(f"Bem-vindo, {user['nome']}")
    st.write("Avaliações atribuídas ao seu e-mail (quando o tutor informou):")
    if not user.get("email"):
        st.info("Seu cadastro não contém e-mail. Peça ao administrador para atualizar ou cadastre usando um e-mail.")
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

# ---------------------------
# Página: Clínica (painel) - simples listagem de clinicas/usuários
# ---------------------------
def tela_clinica_dashboard():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
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
# Roteamento das páginas
# ---------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "user" not in st.session_state:
    st.session_state.user = None
if "eval_info" not in st.session_state:
    st.session_state.eval_info = None

# Top-level routing
page = st.session_state.page

if page == "home":
    tela_inicial()
elif page == "avaliacao_iniciar":
    # proteger: precisa estar logado como tutor
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
else:
    tela_inicial()
# PETdor_full_reset_link.py
import streamlit as st
import sqlite3
import bcrypt
from datetime import datetime, timedelta
from fpdf import FPDF
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import os
import secrets
import matplotlib.pyplot as plt

# -----------------------
# Configuração Streamlit
# -----------------------
st.set_page_config(page_title="🐾 PET DOR", page_icon="🐕", layout="centered")
st.title("🐾 PET DOR")
st.write("Sistema de Avaliação de Dor Animal — painel completo")

# -----------------------
# Config / constantes
# -----------------------
# URL do app (você informou)
APP_URL = "https://petdor.streamlit.app"
# Tempo de expiração do token (horas)
TOKEN_EXP_HOURS = 1

# -----------------------
# DB
# -----------------------
DB_FILE = st.secrets.get("DB_PATH", "petdor.db")

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

conn = conectar()
cur = conn.cursor()

# -----------------------
# E-mail util
# -----------------------
def enviar_email_html(destinatario, assunto, html_body):
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = st.secrets["EMAIL_USER"]
        msg["To"] = destinatario
        msg["Subject"] = assunto

        part = MIMEText(html_body, "html")
        msg.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(st.secrets["SMTP_SERVER"], int(st.secrets["SMTP_PORT"]), context=context) as server:
            server.login(st.secrets["EMAIL_USER"], st.secrets["EMAIL_PASS"])
            server.sendmail(st.secrets["EMAIL_USER"], destinatario, msg.as_string())

        return True
    except Exception as e:
        # não expor stack trace completo ao usuário final
        st.error(f"Erro ao enviar e-mail: {e}")
        return False

def gerar_html_boas_vindas(nome):
    html = f"""
    <div style="font-family:Arial,Helvetica,sans-serif;line-height:1.4;color:#333;">
      <div style="background:#f7f7f9;padding:20px;border-radius:8px">
        <h2 style="color:#2b8aef;margin:0">🐾 Bem-vindo ao PET DOR</h2>
        <p>Olá <strong>{nome}</strong>,</p>
        <p>Seu cadastro foi realizado com sucesso. Acesse o sistema para começar a avaliar seus pets.</p>
        <a href="{APP_URL}" style="display:inline-block;background:#2b8aef;color:#fff;padding:10px 16px;border-radius:6px;text-decoration:none">Abrir PET DOR</a>
        <p style="font-size:12px;color:#666;margin-top:12px">Se você não solicitou este cadastro, ignore este e-mail.</p>
      </div>
    </div>
    """
    return html

def gerar_html_link_reset(nome, token):
    reset_link = f"{APP_URL}/reset?token={token}"
    html = f"""
    <div style="font-family:Arial,Helvetica,sans-serif;color:#333">
      <h3 style="color:#2b8aef">Recuperação de senha - PET DOR</h3>
      <p>Olá <strong>{nome}</strong>,</p>
      <p>Clique no botão abaixo para redefinir sua senha. O link expira em {TOKEN_EXP_HOURS} hora(s).</p>
      <a href="{reset_link}" style="display:inline-block;background:#2b8aef;color:#fff;padding:12px 18px;border-radius:6px;text-decoration:none">Redefinir minha senha</a>
      <p style="color:#666;margin-top:12px">Se você não solicitou, ignore este e-mail.</p>
    </div>
    """
    return html

# -----------------------
# Usuário
# -----------------------
def cadastrar_usuario(nome, email, senha, tipo):
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
    try:
        cur.execute("""
            INSERT INTO usuarios (nome, email, senha, tipo, data_criacao)
            VALUES (?, ?, ?, ?, ?)
        """, (nome, email, senha_hash, tipo, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        html = gerar_html_boas_vindas(nome)
        enviar_email_html(email, "🐾 Bem-vindo ao PET DOR!", html)
        st.success("Cadastro realizado e e-mail enviado!")
    except sqlite3.IntegrityError:
        st.warning("E-mail já cadastrado!")

def autenticar(email, senha):
    cur.execute("SELECT id, nome, senha, tipo, data_criacao FROM usuarios WHERE email = ?", (email,))
    user = cur.fetchone()
    if user and bcrypt.checkpw(senha.encode(), user[2]):
        return user
    return None

# -----------------------
# Recuperação por LINK (token)
# -----------------------
def gerar_token_reset(email):
    # encontra usuário
    cur.execute("SELECT id, nome FROM usuarios WHERE email = ?", (email,))
    u = cur.fetchone()
    if not u:
        st.warning("E-mail não encontrado.")
        return False
    usuario_id, nome = u[0], u[1]
    token = secrets.token_urlsafe(32)
    expires = (datetime.now() + timedelta(hours=TOKEN_EXP_HOURS)).strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO password_resets (usuario_id, token, expires_at, used, created_at) VALUES (?, ?, ?, 0, ?)",
                (usuario_id, token, expires, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    html = gerar_html_link_reset(nome, token)
    enviado = enviar_email_html(email, "🔐 Redefinição de senha - PET DOR", html)
    if enviado:
        st.success("E-mail com link de redefinição enviado. Verifique sua caixa de entrada (ou spam).")
        return True
    else:
        return False

def validar_token(token):
    cur.execute("SELECT id, usuario_id, expires_at, used FROM password_resets WHERE token = ? ORDER BY id DESC LIMIT 1", (token,))
    row = cur.fetchone()
    if not row:
        return None, "Token inválido."
    reset_id, usuario_id, expires_at_str, used = row
    expires_at = datetime.strptime(expires_at_str, "%Y-%m-%d %H:%M:%S")
    if used:
        return None, "Este link já foi utilizado."
    if datetime.now() > expires_at:
        return None, "Este link expirou."
    # retorna usuario_id e reset_id
    return {"usuario_id": usuario_id, "reset_id": reset_id}, None

def resetar_senha_por_token(token, nova_senha):
    valid, err = validar_token(token)
    if err:
        st.error(err)
        return False
    usuario_id = valid["usuario_id"]
    reset_id = valid["reset_id"]
    nova_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt())
    cur.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (nova_hash, usuario_id))
    cur.execute("UPDATE password_resets SET used = 1 WHERE id = ?", (reset_id,))
    conn.commit()
    st.success("Senha redefinida com sucesso! Faça login com sua nova senha.")
    return True

# -----------------------
# Perguntas
# -----------------------
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
    "Meu gato salta até a altura do balcão da cozinha de uma só vez",
    "Meu gato pula para baixo",
    "Meu gato brinca com brinquedos e/ou persegue objetos",
    "Meu gato brinca e interage com outros animais de estimação",
    "Meu gato levanta-se de uma posição de descanso",
    "Meu gato deita-se e/ou senta-se",
    "Meu gato espreguiça-se",
    "Meu gato se limpa normalmente"
]

# -----------------------
# Avaliação e PDF
# -----------------------
def gerar_relatorio_pdf(pet, especie, percentual, usuario_nome):
    pdf = FPDF()
    pdf.add_page()
    # logo (se existir)
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        try:
            pdf.image(logo_path, x=10, y=8, w=30)
        except Exception:
            pass
        pdf.set_xy(50, 10)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Relatório de Dor - PET DOR", ln=True, align="C")
    pdf.ln(8)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, f"Usuário: {usuario_nome}", ln=True)
    pdf.cell(0, 8, f"Nome do Pet: {pet}", ln=True)
    pdf.cell(0, 8, f"Espécie: {especie}", ln=True)
    pdf.cell(0, 8, f"Nível de Dor Estimado: {percentual:.1f}%", ln=True)
    pdf.ln(6)
    if percentual < 30:
        texto = "Baixa probabilidade de dor. Continue observando o comportamento."
    elif percentual < 60:
        texto = "Moderada probabilidade de dor. Avalie e monitore nos próximos dias."
    else:
        texto = "Alta probabilidade de dor. Recomenda-se avaliação veterinária imediata."
    pdf.multi_cell(0, 8, texto)
    filename = f"relatorio_{pet}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

def salvar_avaliacao(usuario_id, usuario_nome, pet_nome, especie, respostas, total, maximo, percentual):
    cur.execute("""
        INSERT INTO avaliacoes (usuario_id, pet_nome, especie, respostas, pontuacao_total, pontuacao_maxima, percentual, data_avaliacao)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (usuario_id, pet_nome, especie, str(respostas), total, maximo, percentual, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

# -----------------------
# Recupera token da URL (se houver)
# -----------------------
query_params = st.experimental_get_query_params()
url_token = None
if "token" in query_params:
    tokens = query_params.get("token")
    if tokens:
        url_token = tokens[0]

# -----------------------
# Interface principal
# -----------------------
# Se existe token na URL, exibe a tela de reset
if url_token:
    st.header("🔐 Redefinir senha")
    st.info("Você abriu o link de redefinição de senha. Escolha uma nova senha abaixo.")
    # valida token para exibir mensagens iniciais
    valid, err = validar_token(url_token)
    if err:
        st.error(err)
        # limpa query params para evitar ficar mostrando a mesma mensagem ao recarregar
        st.experimental_set_query_params()
    else:
        nova_senha = st.text_input("Nova senha", type="password")
        confirma = st.text_input("Confirme a nova senha", type="password")
        if st.button("Redefinir senha"):
            if not nova_senha or not confirma:
                st.warning("Preencha os dois campos.")
            elif nova_senha != confirma:
                st.error("As senhas não conferem.")
            else:
                ok = resetar_senha_por_token(url_token, nova_senha)
                if ok:
                    # limpa token da URL
                    st.experimental_set_query_params()
                    st.success("Senha atualizada. Você pode agora fazer login.")
                    # opcionalmente redirecionar para a home sem query params
                    st.experimental_rerun()
    st.stop()

# Caso contrário, fluxo normal (login / cadastro / painel)
if "usuario_logado" in st.session_state:
    usuario = st.session_state["usuario_logado"]
    st.sidebar.success(f"👋 {usuario['nome']} ({usuario['tipo']})")
    if st.sidebar.button("🚪 Sair"):
        del st.session_state["usuario_logado"]
        st.rerun()

    # Painel principal para usuário logado: tabs
    tab = st.sidebar.radio("Painel", ["Avaliar", "Histórico", "Conta"])
    if tab == "Avaliar":
        st.header("📝 Nova Avaliação")
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
        percentual = (total / maximo) * 100 if maximo else 0

        if st.button("Gerar Relatório"):
            salvar_avaliacao(usuario["id"], usuario["nome"], pet_nome, especie, respostas, total, maximo, percentual)
            pdf_file = gerar_relatorio_pdf(pet_nome, especie, percentual, usuario["nome"])
            with open(pdf_file, "rb") as f:
                st.download_button("⬇️ Baixar Relatório PDF", data=f, file_name=os.path.basename(pdf_file))
            st.success("Relatório gerado e salvo.")
    elif tab == "Histórico":
        st.header("📊 Histórico de Avaliações")
        df = pd.read_sql_query("SELECT id, pet_nome, especie, percentual, data_avaliacao FROM avaliacoes WHERE usuario_id = ? ORDER BY data_avaliacao DESC", conn, params=(usuario["id"],))
        if df.empty:
            st.info("Nenhuma avaliação encontrada.")
        else:
            df["data_avaliacao"] = pd.to_datetime(df["data_avaliacao"])
            st.dataframe(df.rename(columns={"data_avaliacao":"Data", "pet_nome":"Pet", "especie":"Espécie", "percentual":"Percentual"}), use_container_width=True)

            # Gráfico de evolução
            st.subheader("Evolução do percentual ao longo do tempo")
            df_plot = df.sort_values("data_avaliacao")
            plt.figure(figsize=(8,4))
            plt.plot(df_plot["data_avaliacao"], df_plot["percentual"], marker="o")
            plt.title("Percentual estimado de dor")
            plt.xlabel("Data")
            plt.ylabel("Percentual (%)")
            plt.tight_layout()
            st.pyplot(plt)
            plt.clf()
    else:  # Conta
        st.header("⚙️ Conta")
        st.write(f"Nome: **{usuario['nome']}**")
        st.write(f"Tipo: **{usuario['tipo']}**")
        st.write(f"Entrou em: **{usuario.get('data_criacao','-')}**")
        if st.button("Deletar minha conta (permanente)"):
            # Confirmação simples
            confirm = st.text_input("Digite DELETAR para confirmar")
            if confirm == "DELETAR":
                cur.execute("DELETE FROM usuarios WHERE id = ?", (usuario["id"],))
                cur.execute("DELETE FROM avaliacoes WHERE usuario_id = ?", (usuario["id"],))
                conn.commit()
                del st.session_state["usuario_logado"]
                st.success("Conta excluída.")
                st.rerun()

else:
    # Menu quando não logado
    menu = st.sidebar.selectbox("Menu", ["Login", "Cadastrar", "Recuperar senha", "Sobre"])

    if menu == "Cadastrar":
        st.header("Crie sua conta")
        nome = st.text_input("Nome completo")
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        tipo = st.selectbox("Tipo de usuário", ["Tutor", "Veterinário", "Clínica"])
        if st.button("Cadastrar"):
            if nome and email and senha:
                cadastrar_usuario(nome, email, senha, tipo)
            else:
                st.warning("Preencha todos os campos.")

    elif menu == "Login":
        st.header("Login")
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        col1, col2 = st.columns([3,1])
        with col2:
            if st.button("Entrar"):
                user = autenticar(email, senha)
                if user:
                    st.session_state["usuario_logado"] = {
                        "id": user[0],
                        "nome": user[1],
                        "tipo": user[3],
                        "data_criacao": user[4] if len(user) > 4 else None
                    }
                    st.success(f"Bem-vindo, {user[1]}!")
                    st.rerun()
                else:
                    st.error("E-mail ou senha incorretos.")
        st.markdown("Esqueceu a senha? Vá em *Recuperar senha* no menu à esquerda.")

    elif menu == "Recuperar senha":
        st.header("Recuperar senha")
        st.write("Será enviado um e-mail com um link para redefinir sua senha.")
        email_reset = st.text_input("E-mail cadastrado para envio do link")
        if st.button("Enviar link de redefinição"):
            if email_reset:
                gerar_token_reset(email_reset)
            else:
                st.warning("Digite seu e-mail.")

    elif menu == "Sobre":
        st.header("Sobre o PET DOR")
        st.markdown("""
        - Ferramenta para avaliação de dor em cães e gatos.
        - Registro de histórico e geração de PDF com relatório.
        - Recuperação de senha por link seguro enviado por e-mail.
        """)

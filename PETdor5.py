import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# --------------------------
# FUNÇÃO: Envio de e-mail real (GoDaddy)
# --------------------------
def enviar_relatorio_email(tutor_nome, tutor_email, pet_nome, especie, percentual, vet_email, pdf_bytes):
    remetente = "relatorio@petdor.app"
    senha = st.secrets["EMAIL_PASSWORD"]  # lido do arquivo .streamlit/secrets.toml
    servidor_smtp = "smtp.secureserver.net"
    porta = 465  # SSL

    # Montagem dos destinatários (sempre inclui cópia para backup)
    destinatarios = ["relatorio@petdor.app"]
    if tutor_email:
        destinatarios.append(tutor_email)
    if vet_email:
        destinatarios.append(vet_email)

    assunto = f"Relatório PET DOR - {pet_nome} ({especie})"
    corpo = f"""
Olá,

Segue em anexo o relatório de avaliação de dor do pet {pet_nome} ({especie}).
Percentual de dor: {percentual}%

Tutor: {tutor_nome}
E-mail do tutor: {tutor_email or 'não informado'}

Atenciosamente,
Equipe PET DOR
"""

    try:
        msg = MIMEMultipart()
        msg["From"] = remetente
        msg["To"] = ", ".join(destinatarios)
        msg["Subject"] = assunto
        msg.attach(MIMEText(corpo, "plain"))

        # Anexo PDF
        anexo = MIMEApplication(pdf_bytes, _subtype="pdf")
        anexo.add_header("Content-Disposition", "attachment", filename=f"relatorio_{pet_nome}.pdf")
        msg.attach(anexo)

        # Conexão segura
        with smtplib.SMTP_SSL(servidor_smtp, porta) as server:
            server.login(remetente, senha)
            server.send_message(msg)

        st.success(f"✅ Relatório enviado com sucesso para {', '.join(destinatarios)}")

    except Exception as e:
        st.error(f"❌ Falha ao enviar e-mail: {str(e)}")


# --------------------------
# FUNÇÃO: Gerar relatório PDF
# --------------------------
def gerar_relatorio_pdf(tutor_nome, tutor_email, pet_nome, especie, percentual):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    estilos = getSampleStyleSheet()
    conteudo = []

    conteudo.append(Paragraph("Relatório de Avaliação de Dor - PET DOR", estilos["Title"]))
    conteudo.append(Spacer(1, 20))
    conteudo.append(Paragraph(f"Tutor: {tutor_nome}", estilos["Normal"]))
    conteudo.append(Paragraph(f"E-mail: {tutor_email or 'não informado'}", estilos["Normal"]))
    conteudo.append(Paragraph(f"Pet: {pet_nome}", estilos["Normal"]))
    conteudo.append(Paragraph(f"Espécie: {especie}", estilos["Normal"]))
    conteudo.append(Paragraph(f"Nível de dor: {percentual}%", estilos["Normal"]))

    doc.build(conteudo)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


# --------------------------
# FUNÇÃO: Cadastro obrigatório com e-mail
# --------------------------
usuarios = []

def criar_usuario(tipo, nome, email, senha):
    user = {"tipo": tipo, "nome": nome, "email": email, "senha": senha}
    usuarios.append(user)
    return len(usuarios)


# --------------------------
# INTERFACE STREAMLIT
# --------------------------
st.set_page_config(page_title="PET DOR - Sistema de Avaliação de Dor Animal", layout="centered")
st.title("🐾 PET DOR - Sistema de Avaliação de Dor")

menu = st.sidebar.radio("Menu", ["Cadastro", "Avaliação de Dor"])

if menu == "Cadastro":
    st.header("Cadastro de Usuário")
    tipo = st.selectbox("Selecione o tipo de usuário", ["Tutor", "Veterinário", "Clínica"])
    nome = st.text_input("Nome completo")
    email = st.text_input("E-mail (obrigatório)")
    senha = st.text_input("Senha", type="password")

    if st.button("Cadastrar"):
        if not nome or not email or not senha:
            st.warning("⚠️ Nome, e-mail e senha são obrigatórios.")
        else:
            criar_usuario(tipo.lower(), nome.strip(), email.strip(), senha)
            st.success(f"✅ {tipo} cadastrado com sucesso!")

elif menu == "Avaliação de Dor":
    st.header("Relatório de Avaliação de Dor")
    tutor_nome = st.text_input("Nome do tutor")
    tutor_email = st.text_input("E-mail do tutor (obrigatório)")
    pet_nome = st.text_input("Nome do pet")
    especie = st.selectbox("Espécie", ["Cão", "Gato", "Outro"])
    percentual = st.slider("Percentual de dor", 0, 100, 50)
    vet_email = st.text_input("E-mail do veterinário (opcional)")

    if st.button("Gerar e Enviar Relatório"):
        if not tutor_nome or not tutor_email or not pet_nome:
            st.warning("⚠️ Preencha todos os campos obrigatórios (tutor, e-mail e nome do pet).")
        else:
            pdf_bytes = gerar_relatorio_pdf(tutor_nome, tutor_email, pet_nome, especie, percentual)
            enviar_relatorio_email(tutor_nome, tutor_email, pet_nome, especie, percentual, vet_email, pdf_bytes)
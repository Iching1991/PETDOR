# email_sender.py
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

SMTP_SERVER = None
SMTP_PORT = None
EMAIL_USER = None
EMAIL_PASS = None
APP_URL = None

def init_email(smtp_server, smtp_port, email_user, email_pass, app_url):
global SMTP_SERVER, SMTP_PORT, EMAIL_USER, EMAIL_PASS, APP_URL
SMTP_SERVER = smtp_server
SMTP_PORT = int(smtp_port)
EMAIL_USER = email_user
EMAIL_PASS = email_pass
APP_URL = app_url


def send_html_email(destinatario, assunto, html_body):
try:
msg = MIMEMultipart('alternative')
msg['From'] = EMAIL_USER
msg['To'] = destinatario
msg['Subject'] = assunto
msg.attach(MIMEText(html_body, 'html', 'utf-8'))

context = ssl.create_default_context()
with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
server.login(EMAIL_USER, EMAIL_PASS)
server.sendmail(EMAIL_USER, destinatario, msg.as_string())
return True
except Exception as e:
# o app principal já mostra mensagens amigáveis
print('Erro envio email:', e)
return False

# Templates

def template_welcome(nome, link):
return f"""
<!DOCTYPE html><html lang='pt-br'><head><meta charset='utf-8'></head><body>
<div style='font-family:Arial,Helvetica,sans-serif;'>
<h2>🐾 Bem-vindo ao PET DOR</h2>
<p>Olá <b>{nome}</b>, seu cadastro foi confirmado.</p>
<a href='{link}' style='background:#2b8aef;color:#fff;padding:10px 14px;border-radius:6px;text-decoration:none'>Abrir PET DOR</a>
</div></body></html>
"""


def template_reset_link(nome, reset_link, horas=1):
return f"""
<!DOCTYPE html><html lang='pt-br'><head><meta charset='utf-8'></head><body>
<div style='font-family:Arial,Helvetica,sans-serif;'>
<h3>Recuperação de senha - PET DOR</h3>
<p>Olá <b>{nome}</b>, clique no botão para redefinir sua senha (expira em {horas}h).</p>
<a href='{reset_link}' style='background:#2b8aef;color:#fff;padding:12px 16px;border-radius:6px;text-decoration:none'>Redefinir minha senha</a>
</div></body></html>
"""

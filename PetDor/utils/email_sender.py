"""
Utilitário para envio de e-mails HTML
"""
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import logging
from config import SMTP_CONFIG, APP_URL, TOKEN_EXP_HOURS

logger = logging.getLogger(__name__)

def enviar_email_html(destinatario: str, assunto: str, html_body: str) -> bool:
    """
    Envia um e-mail com corpo HTML

    Args:
        destinatario: E-mail do destinatário
        assunto: Assunto do e-mail
        html_body: Corpo do e-mail em HTML

    Returns:
        True se enviado com sucesso, False caso contrário
    """
    try:
        # Verifica configuração SMTP
        if not SMTP_CONFIG["user"] or not SMTP_CONFIG["password"]:
            logger.warning("Configuração SMTP incompleta - e-mail não será enviado")
            return False

        # Cria mensagem com codificação UTF-8
        msg = MIMEMultipart("alternative")
        msg["From"] = SMTP_CONFIG["user"]
        msg["To"] = destinatario

        # ✅ CORREÇÃO: Codifica o assunto em UTF-8
        msg["Subject"] = Header(assunto, 'utf-8').encode()

        # ✅ CORREÇÃO: Garante que o corpo HTML está em UTF-8
        part = MIMEText(html_body, "html", "utf-8")
        msg.attach(part)

        # Configura SSL e envia
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(
            SMTP_CONFIG["server"],
            SMTP_CONFIG["port"],
            context=context,
        ) as server:
            server.login(SMTP_CONFIG["user"], SMTP_CONFIG["password"])

            # ✅ CORREÇÃO: Envia com codificação UTF-8
            server.send_message(msg)

        logger.info(f"E-mail enviado com sucesso para {destinatario}: {assunto}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Erro de autenticação SMTP: {e}")
        logger.error("Verifique as credenciais no arquivo .streamlit/secrets.toml")
        return False

    except smtplib.SMTPRecipientsRefused as e:
        logger.error(f"E-mail rejeitado pelo servidor: {e}")
        return False

    except smtplib.SMTPException as e:
        logger.error(f"Erro SMTP: {e}")
        return False

    except UnicodeEncodeError as e:
        logger.error(f"Erro de codificação UTF-8: {e}")
        return False

    except Exception as e:
        logger.error(f"Erro inesperado ao enviar e-mail: {e}")
        return False

def gerar_html_boas_vindas(nome: str) -> str:
    """
    Gera HTML para e-mail de boas-vindas

    Args:
        nome: Nome do usuário

    Returns:
        String HTML formatada
    """
    # ✅ CORREÇÃO: Garante que a string é UTF-8
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title>Bem-vindo ao PET DOR</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f7fafc; padding: 20px; margin: 0;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; 
                    padding: 30px; border: 1px solid #e2e8f0; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">

            <!-- Header -->
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #2b8aef; margin: 0; font-size: 2.2rem;">🐾 PET DOR</h1>
                <p style="color: #718096; margin: 5px 0 0 0; font-size: 1.1rem;">
                    Sistema de Avaliação de Dor Animal
                </p>
            </div>

            <!-- Conteúdo -->
            <div style="background: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 25px;">
                <h2 style="color: #2d3748; margin-top: 0; font-size: 1.5rem;">
                    Bem-vindo, <strong>{nome}</strong>!
                </h2>

                <p style="color: #4a5568; line-height: 1.6; margin-bottom: 20px;">
                    Seu cadastro foi realizado com sucesso! Agora você pode utilizar o PET DOR
                    para avaliar a dor dos seus pacientes ou pets de forma organizada e científica.
                </p>

                <p style="color: #4a5568; line-height: 1.6; margin-bottom: 25px;">
                    <strong>Funcionalidades disponíveis:</strong><br>
                    • Questionários específicos por espécie<br>
                    • Cálculo automático de percentual de dor<br>
                    • Histórico completo com gráficos<br>
                    • Relatórios profissionais em PDF
                </p>

                <!-- Botão -->
                <div style="text-align: center; margin: 25px 0;">
                    <a href="{APP_URL}" 
                       style="display: inline-block; background: linear-gradient(135deg, #2b8aef, #1e40af); 
                              color: #ffffff; padding: 15px 30px; border-radius: 8px; 
                              text-decoration: none; font-weight: 600; font-size: 1.1rem;
                              box-shadow: 0 4px 15px rgba(43, 138, 239, 0.3);">
                        Acessar PET DOR
                    </a>
                </div>

                <p style="color: #718096; font-size: 0.9rem; text-align: center; margin-top: 30px;">
                    Se você não reconhece este cadastro, simplesmente ignore este e-mail.<br>
                    Sua conta permanecerá segura.
                </p>
            </div>

            <!-- Footer -->
            <div style="text-align: center; padding-top: 25px; border-top: 1px solid #e2e8f0;">
                <p style="color: #a0aec0; font-size: 0.85rem; margin: 0;">
                    © 2024 PET DOR - Sistema de Avaliação de Dor Animal<br>
                    <a href="mailto:suporte@petdor.com" style="color: #2b8aef;">suporte@petdor.com</a>
                </p>
            </div>

        </div>
    </body>
    </html>
    """

def gerar_html_reset_senha(nome: str, token: str) -> str:
    """
    Gera HTML para e-mail de reset de senha

    Args:
        nome: Nome do usuário
        token: Token de reset

    Returns:
        String HTML formatada
    """
    reset_link = f"{APP_URL}?token={token}"

    # ✅ CORREÇÃO: Garante que a string é UTF-8
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title>Redefinição de Senha - PET DOR</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f7fafc; padding: 20px; margin: 0;">
        <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; 
                    padding: 30px; border: 1px solid #e2e8f0; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">

            <!-- Header -->
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #2b8aef; margin: 0; font-size: 2.2rem;">🐾 PET DOR</h1>
                <p style="color: #718096; margin: 5px 0 0 0; font-size: 1.1rem;">
                    Recuperação de Senha
                </p>
            </div>

            <!-- Conteúdo -->
            <div style="background: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 25px;">
                <h2 style="color: #2d3748; margin-top: 0; font-size: 1.5rem;">
                    Olá, <strong>{nome}</strong>!
                </h2>

                <p style="color: #4a5568; line-height: 1.6; margin-bottom: 20px;">
                    Recebemos uma solicitação para redefinir sua senha no PET DOR.
                    Para criar uma nova senha, clique no botão abaixo.
                </p>

                <p style="color: #4a5568; line-height: 1.6; margin-bottom: 15px;">
                    <strong>Importante:</strong> Este link é válido por apenas <strong>{TOKEN_EXP_HOURS} hora(s)</strong>.
                </p>

                <!-- Botão -->
                <div style="text-align: center; margin: 25px 0;">
                    <a href="{reset_link}" 
                       style="display: inline-block; background: linear-gradient(135deg, #2b8aef, #1e40af); 
                              color: #ffffff; padding: 15px 30px; border-radius: 8px; 
                              text-decoration: none; font-weight: 600; font-size: 1.1rem;
                              box-shadow: 0 4px 15px rgba(43, 138, 239, 0.3);">
                        Redefinir Minha Senha
                    </a>
                </div>

                <p style="color: #4a5568; line-height: 1.6; margin-bottom: 20px; font-size: 0.95rem;">
                    Se o botão não funcionar, copie e cole este link no seu navegador:<br>
                    <a href="{reset_link}" style="color: #2b8aef; word-break: break-all;">{reset_link}</a>
                </p>

                <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 6px; 
                           padding: 15px; margin: 20px 0;">
                    <p style="color: #856404; margin: 0; font-size: 0.9rem;">
                        <strong>⚠️ Segurança:</strong> Se você não solicitou esta redefinição, 
                        ignore este e-mail. Sua senha permanecerá inalterada e sua conta está segura.
                    </p>
                </div>

                <p style="color: #718096; font-size: 0.9rem; text-align: center; margin-top: 30px;">
                    Precisa de ajuda? <a href="mailto:suporte@petdor.com" style="color: #2b8aef;">Entre em contato</a>
                </p>
            </div>

            <!-- Footer -->
            <div style="text-align: center; padding-top: 25px; border-top: 1px solid #e2e8f0;">
                <p style="color: #a0aec0; font-size: 0.85rem; margin: 0;">
                    © 2024 PET DOR - Sistema de Avaliação de Dor Animal<br>
                    <a href="mailto:suporte@petdor.com" style="color: #2b8aef;">suporte@petdor.com</a>
                </p>
            </div>

        </div>
    </body>
    </html>
    """

def testar_configuracao_email() -> tuple:
    """
    Testa se a configuração de e-mail está funcionando
    Útil para debug

    Returns:
        (funciona, mensagem)
    """
    try:
        if not SMTP_CONFIG["user"] or not SMTP_CONFIG["password"]:
            return False, "Configuração SMTP incompleta"

        # Testa conexão básica
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_CONFIG["server"], SMTP_CONFIG["port"], context=context) as server:
            server.login(SMTP_CONFIG["user"], SMTP_CONFIG["password"])

        return True, "Configuração de e-mail OK"

    except Exception as e:
        return False, f"Erro na configuração: {str(e)}"


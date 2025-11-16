"""
Sistema de recuperação e reset de senha
"""
import secrets
import bcrypt
from datetime import datetime, timedelta
from typing import Tuple, Optional
import logging

from database.connection import get_db
from config import TOKEN_EXPIRATION, MAX_RESET_ATTEMPTS_PER_DAY
from utils.email_sender import enviar_email_html, gerar_html_reset_senha
from utils.validators import validar_senha, validar_email

logger = logging.getLogger(__name__)


def _get_usuario_por_email(email: str):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, nome, email FROM usuarios WHERE email = ? AND ativo = 1",
            (email.lower().strip(),),
        )
        return cur.fetchone()


def _contar_resets_ultimas_24h(usuario_id: int) -> int:
    limite = datetime.now() - timedelta(days=1)
    limite_str = limite.strftime("%Y-%m-%d %H:%M:%S")
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COUNT(*) AS total
            FROM password_resets
            WHERE usuario_id = ? AND created_at > ?
            """,
            (usuario_id, limite_str),
        )
        row = cur.fetchone()
    return row["total"] if row else 0


def gerar_token_reset(email: str) -> Tuple[bool, str]:
    """
    Gera token para reset de senha e envia e-mail.
    Retorna (sucesso, mensagem amigável).
    """
    ok, msg = validar_email(email)
    if not ok:
        return False, msg

    user = _get_usuario_por_email(email)
    # Segurança: não revela se email existe ou não
    if not user:
        logger.info(f"Solicitação de reset para email não cadastrado: {email}")
        return True, (
            "Se o e-mail estiver cadastrado, um link de redefinição será enviado. "
            "Verifique sua caixa de entrada (e spam)."
        )

    usuario_id, nome, _ = user["id"], user["nome"], user["email"]

    # Rate limit
    tentativas = _contar_resets_ultimas_24h(usuario_id)
    if tentativas >= MAX_RESET_ATTEMPTS_PER_DAY:
        return False, (
            f"Você já solicitou redefinição {MAX_RESET_ATTEMPTS_PER_DAY} vezes nas últimas 24h. "
            "Tente novamente mais tarde."
        )

    token = secrets.token_urlsafe(32)
    expires_at = (datetime.now() + TOKEN_EXPIRATION).strftime("%Y-%m-%d %H:%M:%S")
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO password_resets (usuario_id, token, expires_at, used, created_at)
                VALUES (?, ?, ?, 0, ?)
                """,
                (usuario_id, token, expires_at, created_at),
            )
            conn.commit()

        html = gerar_html_reset_senha(nome, token)
        ok_email = enviar_email_html(email, "🔐 Redefinição de senha - PET DOR", html)

        if not ok_email:
            return False, "Erro ao enviar e-mail de recuperação. Tente novamente mais tarde."

        logger.info(f"Token de reset gerado para usuário {usuario_id}")
        return True, (
            "Se o e-mail estiver cadastrado, você receberá um link de redefinição em instantes. "
            "Verifique seu e-mail (e a pasta de spam)."
        )

    except Exception as e:
        logger.error(f"Erro ao gerar token de reset: {e}")
        return False, "Erro ao processar solicitação. Tente novamente."


def validar_token(token: str) -> Tuple[Optional[int], Optional[str]]:
    """
    Valida token de reset.
    Retorna (usuario_id erro). Se erro for None, token é válido.
    """
    if not token:
        return None, "Token inválido."

    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT usuario_id, expires_at, used
                FROM password_resets
                WHERE token = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (token,),
            )
            row = cur.fetchone()

        if not row:
            return None, "Token inválido ou inexistente."

        if row["used"]:
            return None, "Este link já foi utilizado."

        expires_at = datetime.strptime(row["expires_at"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() > expires_at:
            return None, "Este link expirou. Solicite um novo."

        return row["usuario_id"], None

    except Exception as e:
        logger.error(f"Erro ao validar token: {e}")
        return None, "Erro ao validar link. Tente novamente."


def resetar_senha(token: str, nova_senha: str) -> Tuple[bool, str]:
    """
    Reseta senha a partir de um token válido.
    Retorna (sucesso, mensagem)
    """
    usuario_id, erro = validar_token(token)
    if erro:
        return False, erro

    ok, msg = validar_senha(nova_senha)
    if not ok:
        return False, msg

    nova_hash = bcrypt.hashpw(nova_senha.encode("utf-8"), bcrypt.gensalt())

    try:
        with get_db() as conn:
            cur = conn.cursor()
            # Atualiza senha do usuário
            cur.execute(
                "UPDATE usuarios SET senha = ? WHERE id = ?",
                (nova_hash, usuario_id),
            )
            # Marca token como usado
            cur.execute(
                "UPDATE password_resets SET used = 1 WHERE token = ?",
                (token,),
            )
            conn.commit()

        logger.info(f"Senha redefinida para usuário id={usuario_id}")
        return True, "Senha redefinida com sucesso! Você já pode efetuar login com a nova senha."
    except Exception as e:
        logger.error(f"Erro ao redefinir senha: {e}")
        return False, "Erro ao redefinir senha. Tente novamente."

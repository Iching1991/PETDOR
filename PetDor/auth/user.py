"""
Gerenciamento de usuários e autenticação
"""
import bcrypt
from datetime import datetime
from typing import Optional, Dict, Tuple
import logging

from database.connection import get_db
from utils.validators import validar_email, validar_senha, validar_nome
from utils.email_sender import enviar_email_html, gerar_html_boas_vindas

logger = logging.getLogger(__name__)


def cadastrar_usuario(nome: str, email: str, senha: str, tipo: str) -> Tuple[bool, str]:
    """
    Cadastra novo usuário no sistema.
    Retorna (sucesso, mensagem)
    """
    # Validações básicas
    ok, msg = validar_nome(nome)
    if not ok:
        return False, msg

    ok, msg = validar_email(email)
    if not ok:
        return False, msg

    ok, msg = validar_senha(senha)
    if not ok:
        return False, msg

    # Hash da senha
    senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())

    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO usuarios (nome, email, senha, tipo, data_criacao, ativo)
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                (
                    nome.strip(),
                    email.lower().strip(),
                    senha_hash,
                    tipo,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            conn.commit()

        # Envia e-mail de boas-vindas (sem travar o fluxo se falhar)
        try:
            html = gerar_html_boas_vindas(nome)
            enviar_email_html(email, "🐾 Bem-vindo ao PET DOR!", html)
        except Exception as e:
            logger.warning(f"Falha ao enviar e-mail de boas-vindas: {e}")

        logger.info(f"Usuário cadastrado: {email}")
        return True, "Cadastro realizado com sucesso! Verifique seu e-mail."

    except Exception as e:
        logger.error(f"Erro ao cadastrar usuário: {e}")
        # Verifica se é erro de e-mail duplicado
        if "UNIQUE constraint failed" in str(e) or "UNIQUE constraint" in str(e):
            return False, "Este e-mail já está cadastrado."
        return False, "Erro ao realizar cadastro. Tente novamente mais tarde."


def autenticar(email: str, senha: str) -> Optional[Dict]:
    """
    Autentica usuário pelo e-mail e senha.
    Retorna dicionário com dados do usuário ou None.
    """
    ok, _ = validar_email(email)
    if not ok:
        return None

    try:
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, nome, email, senha, tipo, data_criacao, ativo
                FROM usuarios
                WHERE email = ?
                """,
                (email.lower().strip(),),
            )
            row = cur.fetchone()

        if not row:
            logger.warning(f"Tentativa de login com e-mail inexistente: {email}")
            return None

        if not row["ativo"]:
            logger.warning(f"Login em conta desativada: {email}")
            return None

        senha_hash = row["senha"]
        if not bcrypt.checkpw(senha.encode("utf-8"), senha_hash):
            logger.warning(f"Senha incorreta para: {email}")
            return None

        logger.info(f"Login bem-sucedido: {email}")
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "tipo": row["tipo"],
            "data_criacao": row["data_criacao"],
        }

    except Exception as e:
        logger.error(f"Erro na autenticação: {e}")
        return None


def deletar_usuario(usuario_id: int) -> Tuple[bool, str]:
    """
    "Deleta" usuário: faz soft delete (ativo = 0) e pode, se quiser,
    limpar avaliações associadas.
    Retorna (sucesso, mensagem)
    """
    try:
        with get_db() as conn:
            cur = conn.cursor()
            # Soft delete
            cur.execute(
                "UPDATE usuarios SET ativo = 0 WHERE id = ?",
                (usuario_id,),
            )

            # Se quiser excluir avaliações também (hard delete):
            # cur.execute("DELETE FROM avaliacoes WHERE usuario_id = ?", (usuario_id,))

            conn.commit()

        logger.info(f"Usuário marcado como inativo: id={usuario_id}")
        return True, "Conta excluída com sucesso."

    except Exception as e:
        logger.error(f"Erro ao excluir usuário: {e}")
        return False, "Erro ao excluir conta. Tente novamente."

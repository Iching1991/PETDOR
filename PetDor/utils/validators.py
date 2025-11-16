"""
Funções de validação de entrada
"""
import re
from typing import Tuple
from config import PASSWORD_MIN_LENGTH


def validar_email(email: str) -> Tuple[bool, str]:
    if not email:
        return False, "E-mail é obrigatório."

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, "Formato de e-mail inválido."

    return True, ""


def validar_senha(senha: str) -> Tuple[bool, str]:
    if not senha:
        return False, "Senha é obrigatória."

    if len(senha) < PASSWORD_MIN_LENGTH:
        return False, f"Senha deve ter pelo menos {PASSWORD_MIN_LENGTH} caracteres."

    # Se quiser reforçar a segurança:
    # if not any(c.isdigit() for c in senha):
    #     return False, "A senha deve conter pelo menos um número."
    # if not any(c.isupper() for c in senha):
    #     return False, "A senha deve conter pelo menos uma letra maiúscula."

    return True, ""


def validar_nome(nome: str) -> Tuple[bool, str]:
    if not nome or len(nome.strip()) < 3:
        return False, "Nome deve ter pelo menos 3 caracteres."
    return True, ""


def senhas_conferem(senha: str, confirmacao: str) -> Tuple[bool, str]:
    if senha != confirmacao:
        return False, "As senhas não conferem."
    return True, ""

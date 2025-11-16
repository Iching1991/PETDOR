"""
Módulo de banco de dados do PET DOR
"""
from database.connection import init_database, get_db
from database.models import (
    salvar_avaliacao,
    buscar_avaliacoes_usuario,
    buscar_avaliacao_detalhada,
    deletar_avaliacao,
    get_estatisticas_usuario
)

__all__ = [
    'init_database',
    'get_db',
    'salvar_avaliacao',
    'buscar_avaliacoes_usuario',
    'buscar_avaliacao_detalhada',
    'deletar_avaliacao',
    'get_estatisticas_usuario'
]

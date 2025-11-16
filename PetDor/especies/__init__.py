"""
Módulo de configurações de espécies para avaliação de dor
Sistema modular - um arquivo .py por espécie
"""
from especies.base import EspecieConfig, Pergunta
from especies.loader import (
 get_especies_nomes,
    get_especie_config,
    get_escala_labels,
    ESPECIES_DISPONIVEIS
)

__all__ = [
    'EspecieConfig',
    'Pergunta',
    'get_especies_nomes',
    'get_especie_config',
    'get_escala_labels',
    'ESPECIES_DISPONIVEIS'
]

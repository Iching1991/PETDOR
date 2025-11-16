"""
Carregador dinâmico de configurações de espécies
Sistema modular - fácil adicionar novas espécies
"""
from typing import Dict, List
from especies.base import EspecieConfig
from especies.caes import CONFIG_CAES
from especies.gatos import CONFIG_GATOS

# Registro central de todas as espécies disponíveis
ESPECIES_DISPONIVEIS: Dict[str, EspecieConfig] = {
    "Cachorro": CONFIG_CAES,
    "Gato": CONFIG_GATOS,
    # Para adicionar nova espécie, basta:
    # 1. Criar especies/nova_especie.py
    # 2. Adicionar aqui: "Nova Espécie": CONFIG_NOVA_ESP
}

def get_especies_nomes() -> List[str]:
    """Retorna lista de nomes de espécies disponíveis"""
    return(ESPECIES_DISPONIVEIS.keys())

def get_especie_config(nome: str) -> EspecieConfig:
    """
    Retorna configuração de uma espécie
    Raises KeyError se espécie existir
    """
    if nome not in ESPECIES_DISPONIVEIS:
        raise KeyError(f"Espécie '{nome}' não encontrada. Disponíveis: {get_especies_nomes()}")

    return ESPECIES_DISPONIVEIS[nome]

def get_escala_labels(escala_min: int, escala_max: int) -> Dict[int, str]:
    """
    Gera labels para a escala de avaliação
    """
    if escala_max == 4:
        return {
            0: "0 - Nunca",
            1: "1 - Raramente",
            2: "2 - Às vezes", 
            3: "3 - Frequentemente",
            4: "4 - Sempre"
        }
    elif escala_max == 7:
        return {
            0: "0 - Nunca",
            1: "1 - Muito raramente",
            2: "2 - Raramente",
            3: "3 - Às vezes",
            4: "4 - Regularmente",
            5: "5 - Frequentemente",
            6: "6 - Muito frequentemente",
            7: "7 - Sempre"
        }
    else:
        return {i: str(i) for i in range(escala_min, escala_max + 1)}

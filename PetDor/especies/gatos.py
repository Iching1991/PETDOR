"""
🐈 Configuração de avaliação para GATOS
Escala: 0 a 4 (baseado em Feline Musculoskeletal Pain Index - FMPI)
"""
from especies.base import EspecieConfig, Pergunta

CONFIG_GATOS = EspecieConfig(
    nome="Gato",
    escala_min=0,
    escala_max=4,
    descricao="Avaliação de dor em gatos - Escala de 0 (nunca) a 4 (sempre)",
    perguntas=[
        # Mobilidade Vertical
        Pergunta(texto="Meu gato salta para cima (móveis, prateleiras)", invertida=False),
        Pergunta(texto="Meu gato salta até a altura do balcão da cozinha de uma só vez", invertida=False),
        Pergunta(texto="Meu gato pula para baixo de móveis", invertida=False),

        # Atividade e Brincadeira
        Pergunta(texto="Meu gato brinca com brinquedos e/ou persegue objetos", invertida=False),
       unta(texto="Meu gato brinca e interage com outros animais de estimação", invertida=False),

        # Mobilidade Básica
        Pergunta(texto="Meu gato levanta-se de uma posição de descanso facilmente", invertida=False),
        Pergunta(texto="Meu gato deita-se e/ou senta-se sem hesitação", invertida=False),
        Pergunta(texto="Meu gato espreguiça-se normalmente", invertida=False),

        # Higiene e Autocuidado
        Pergunta(texto="Meu gato se limpa (grooming) normalmente", invertida=False),
    ]
)

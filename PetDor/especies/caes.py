"""
🐕 Configuração de avaliação para CÃES
Escala: 0 a 7 (baseada em CBPI e Glasgow Composite Pain Scale)
"""
from especies.base import EspecieConfig, Pergunta

CONFIG_CAES = EspecieConfig(
    nome="Cachorro",
    escala_min=0,
    escala_max=7,
    descricao="Avaliação de dor em cães - Escala de 0 (nunca) a 7 (sempre)",
    perguntas=[
        # Energia e Atividade
        Pergunta(texto="Meu cão pouca energia", invertida=True),
        Pergunta(texto="Meu cão foi brincalhão", invertida=False),
        Pergunta(texto="Meu cão fez as suas atividades favoritas", invertida=False),

        # Alimentação
        Pergunta(texto="O apetite do meu cão reduziu", invertida=True),
        Pergunta(texto="Meu cão comeu normalmente a sua comida favorita", invertida=False),

        # Mobilidade
        Pergunta(texto="Meu cão reluta para levantar", invertida=True),
        Pergunta(texto="Meu cão teve problemas para levantar-se ou deitar-se", invertida=True),
        Pergunta(texto="Meu cão teve problemas para caminhar", invertida=True),
        Pergunta(texto="Meu cão caiu ou perdeu o equilíbrio", invertida=True),

        # Comportamento Social
        Pergunta(texto="Meu cão gosta de estar perto de mim", invertida=False),
        Pergunta(texto="Meu cão mostrou uma quantidade normal de afeto", invertida=False),
        Pergunta(texto="Meu cão gostou de ser tocado ou acariciado", invertida=False),

        # Comportamento Geral
        Pergunta(texto="Meu cão agiu normalmente", invertida=False),
        Pergunta(texto="Meu cão teve problemas para ficar confortável", invertida=True),

        # Sono
        Pergunta(texto="Meu cão dormiu bem durante a noite", invertida=False),
    ]
)

"""
Classe base para configuração de espécies
"""
from dataclasses import dataclass
from typing import List

@dataclass
class Pergunta:
    """Representa uma pergunta de avaliação"""
    texto: str
    invertida: bool = False  # Se True, pontuação é invertida (ex: "teve problemas")

@dataclass
class EspecieConfig:
    """Configuração de uma espécie"""
    nome: str
    escala_min: int
    escala_max: int
    perguntas: List[Pergunta]
    descricao: str = ""

    def get_pontuacao_maxima(self) -> int:
        """Retorna pontuação máxima possível"""
        return len(self.perguntas) * self.escala_max

    def calcular_percentual(self, pontuacao_total: int) -> float:
        """Calcula percentual de dor"""
        max_pontos = self.get_pontuacao_maxima()
        return (pontuacao_total / max_pontos * 100) if max_pontos > 0 else 0.0

    def get_labels_escala(self) -> dict:
        """Retorna labels para a escala de avaliação"""
        if self.escala_max == 4:
            return {
                0: "0 - Nunca",
                1: "1 - Raramente", 
                2: "2 - Às vezes",
                3: "3 - Frequentemente",
                4: "4 - Sempre"
            }
        elif self.escala_max == 7:
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
            return {i: f"{i}" for i in range(self.escala_min, self.escala_max + 1)}

"""
Modelos e operações de banco de dados
"""
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json
import logging
from database.connection import get_db

logger = logging.getLogger(__name__)

def salvar_avaliacao(
    usuario_id: int,
    pet_nome: str,
    especie: str,
    respostas: List[int],
    pontuacao_total: int,
    pontuacao_maxima: int,
    percentual: float
) -> Tuple[bool, str]:
    """Salva uma nova avaliação"""
    try:
        with get_db() as conn:
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO avaliacoes (
                    usuario_id, pet_nome, especie, respostas,
                    pontuacao_total, pontuacao_maxima, percentual,
                    data_avaliacao
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                usuario_id,
                pet_nome.strip(),
                especie,
                json.dumps(respostas),
                pontuacao_total,
                pontuacao_maxima,
                percentual,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            conn.commit()

        logger.info(f"Avaliação salva: Usuário {usuario_id}")
        return True, "Avaliação salva com sucesso!"

    except Exception as e:
        logger.error(f"Erro ao salvar avaliação: {e}")
        return False, "Erro ao salvar avaliação."

def buscar_avaliacoes_usuario(usuario_id: int) -> List[Dict]:
    """Busca todas as avaliações de um usuário"""
    try:
        with get_db() as conn:
            cur = conn.cursor()

            cur.execute("""
                SELECT 
                    id, pet_nome, especie, pontuacao_total,
                    pontuacao_maxima, percentual, data_avaliacao
                FROM avaliacoes
                WHERE usuario_id = ?
                ORDER BY data_avaliacao DESC
            """, (usuario_id,))

            rows = cur.fetchall()

            return [dict(row) for row in rows]

    except Exception as e:
        logger.error(f"Erro ao buscar avaliações: {e}")
        return []

def buscar_avaliacao_detalhada(avaliacao_id: int, usuario_id: int) -> Optional[Dict]:
    """Busca detalhes completos de uma avaliação"""
    try:
        with get_db() as conn:
            cur = conn.cursor()

            cur.execute("""
                SELECT *
                FROM avaliacoes
                WHERE id = ? AND usuario_id = ?
            """, (avaliacao_id, usuario_id))

            row = cur.fetchone()

            if row:
                data = dict(row)
                data['respostas'] = json.loads(data['respostas'])
                return data

            return None

    except Exception as e:
        logger.error(f"Erro ao buscar avaliação detalhada: {e}")
        return None

def deletar_avaliacao(avaliacao_id: int, usuario_id: int) -> Tuple[bool, str]:
    """Deleta uma avaliação"""
    try:
        with get_db() as conn:
            cur = conn.cursor()

            cur.execute("""
                DELETE FROM avaliacoes
                WHERE id = ? AND usuario_id = ?
            """, (avaliacao_id, usuario_id))

            conn.commit()

            if cur.rowcount > 0:
                logger.info(f"Avaliação deletada: ID {avaliacao_id}")
                return True, "Avaliação excluída com sucesso."
            else:
                return False, "Avaliação não encontrada."

    except Exception as e:
        logger.error(f"Erro ao deletar avaliação: {e}")
        return False, "Erro ao excluir avaliação."

def get_estatisticas_usuario(usuario_id: int) -> Dict:
    """Retorna estatísticas das avaliações do usuário"""
    try:
        with get_db() as conn:
            cur = conn.cursor()

            cur.execute("""
                SELECT 
                    COUNT(*) as total_avaliacoes,
                    COUNT(DISTINCT pet_nome) as total_pets,
                    AVG(percentual) as media_percentual,
                    MAX(percentual) as max_percentual,
                    MIN(percentual) as min_percentual
                FROM avaliacoes
                WHERE usuario_id = ?
            """, (usuario_id,))

            row = cur.fetchone()

            return dict(row) if row else {}

    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        return {}

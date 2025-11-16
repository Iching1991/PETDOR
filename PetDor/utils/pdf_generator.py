"""
Gerador de relatórios PDF
"""
from fpdf import FPDF
from datetime import datetime
import os
import logging
from config import get_nivel_dor

logger = logging.getLogger(__name__)


class RelatorioPDF(FPDF):
    def header(self):
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            try:
                self.image(logo_path, x=10, y=8, w=30)
            except Exception:
                pass
        self.set_font("Arial", "B", 16)
        self.set_text_color(43, 138, 239)
        self.cell(0, 10, "PET DOR", ln=True, align="C")
        self.set_font("Arial", "", 11)
        self.set_text_color(100, 100, 100)
        self.cell(0, 6, "Relatório de Avaliação de Dor", ln=True, align="C")
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(
            0,
            10,
            f"Página {self.page_no()} | PET DOR - Sistema de Avaliação de Dor Animal",
            align="C",
        )


def gerar_relatorio_pdf(
    pet_nome: str,
    especie: str,
    percentual: float,
    pontuacao_total: int,
    pontuacao_maxima: int,
    usuario_nome: str,
    data_avaliacao: str = None,
    idade: float = None,
) -> str:
    """
    Gera relatório PDF da avaliação.
    Retorna o caminho do arquivo gerado.
    """
    try:
        pdf = RelatorioPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        if not data_avaliacao:
            data_avaliacao = datetime.now().strftime("%d/%m/%Y %H:%M")

        # Info paciente
        pdf.set_font("Arial", "B", 13)
        pdf.set_text_color(45, 55, 72)
        pdf.cell(0, 8, "Informações do Paciente", ln=True)
        pdf.ln(2)

        pdf.set_font("Arial", "", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(50, 6, "Data da Avaliação:", 0)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 6, data_avaliacao, ln=True)

        pdf.set_font("Arial", "", 11)
        pdf.cell(50, 6, "Responsável:", 0)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 6, usuario_nome, ln=True)

        pdf.set_font("Arial", "", 11)
        pdf.cell(50, 6, "Nome do Paciente:", 0)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 6, pet_nome, ln=True)

        pdf.set_font("Arial", "", 11)
        pdf.cell(50, 6, "Espécie:", 0)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 6, especie, ln=True)

        if idade is not None:
            pdf.set_font("Arial", "", 11)
            pdf.cell(50, 6, "Idade:", 0)
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 6, f"{idade} anos", ln=True)

        pdf.ln(8)

        # Resultado
        pdf.set_font("Arial", "B", 13)
        pdf.set_text_color(45, 55, 72)
        pdf.cell(0, 8, "Resultado da Avaliação", ln=True)
        pdf.ln(2)

        nivel = get_nivel_dor(percentual)

        if percentual < 30:
            pdf.set_fill_color(40, 167, 69)
        elif percentual < 60:
            pdf.set_fill_color(255, 193, 7)
        else:
            pdf.set_fill_color(220, 53, 69)

        pdf.set_font("Arial", "B", 22)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 16, f"Nível de dor: {percentual:.1f}%", ln=True, fill=True, align="C")
        pdf.ln(4)

        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 6, f"Pontuação: {pontuacao_total} / {pontuacao_maxima}", ln=True)

        if percentual < 30:
            classificacao = "BAIXO"
        elif percentual < 60:
            classificacao = "MODERADO"
        else:
            classificacao = "ALTO"

        pdf.set_font("Arial", "B", 11)
        pdf.set_text_color(45, 55, 72)
        pdf.cell(0, 8, f"Classificação: {classificacao}", ln=True)

        pdf.ln(6)

        # Recomendações
        pdf.set_font("Arial", "B", 13)
        pdf.set_text_color(45, 55, 72)
        pdf.cell(0, 8, "Recomendação Clínica", ln=True)
        pdf.ln(2)

        pdf.set_font("Arial", "", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 5, nivel["texto"])

        pdf.ln(8)

        pdf.set_font("Arial", "I", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.multi_cell(
            0,
            4,
            "IMPORTANTE: Este relatório é uma ferramenta de triagem e não substitui a "
            "avaliação clínica de um médico veterinário. Em caso de dúvidas, sinais de dor "
            "intensa ou piora no quadro, procure atendimento veterinário imediatamente.",
        )

        # Salva
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_pet = pet_nome.replace(" ", "_")
        filename = f"petdor_{safe_pet}_{timestamp}.pdf"

        os.makedirs("temp", exist_ok=True)
        filepath = os.path.join("temp", filename)
        pdf.output(filepath)
        logger.info(f"PDF gerado: {filepath}")
        return filepath

    except Exception as e:
        logger.error(f"Erro ao gerar PDF: {e}")
        raise


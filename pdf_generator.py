# pdf_generator.py
from fpdf import FPDF
import os
from datetime import datetime

LOGO_PATH = 'assets/logo.png'

def gerar_relatorio_pdf(pet, especie, percentual, usuario_nome):
pdf = FPDF()
pdf.add_page()
if os.path.exists(LOGO_PATH):
try:
pdf.image(LOGO_PATH, x=10, y=8, w=30)
except Exception:
pass
pdf.set_xy(50, 10)
pdf.set_font('Arial', 'B', 16)
pdf.cell(0, 10, 'Relatório de Dor - PET DOR', ln=True, align='C')
pdf.ln(8)
pdf.set_font('Arial', size=12)
pdf.cell(0, 8, f'Usuário: {usuario_nome}', ln=True)
pdf.cell(0, 8, f'Nome do Pet: {pet}', ln=True)
pdf.cell(0, 8, f'Espécie: {especie}', ln=True)
pdf.cell(0, 8, f'Nível de Dor Estimado: {percentual:.1f}%', ln=True)
pdf.ln(6)
if percentual < 30:
texto = 'Baixa probabilidade de dor. Continue observando.'
elif percentual < 60:
texto = 'Probabilidade moderada de dor. Monitore.'
else:
texto = 'Alta probabilidade — consulte um veterinário.'
pdf.multi_cell(0, 8, texto)
filename = f'relatorio_{pet}_{datetime.now().strftime("%Y%m%d%H%M%S")}.pdf'
pdf.output(filename)
return filename

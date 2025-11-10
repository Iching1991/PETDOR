import streamlit as st
import time
import threading

# ===========================
# CONFIGURAÇÕES INICIAIS
# ===========================
st.set_page_config(
    page_title="PETDOR 🐾",
    layout="wide",
    page_icon="🐕"
)

st.title("🐾 PETDOR — Avaliação de Dor em Pets")

# ===========================
# FUNÇÃO DE AVALIAÇÃO
# ===========================
def calcular_dor(respostas, escala_max):
    soma = sum(respostas)
    max_total = len(respostas) * escala_max
    percentual = (soma / max_total) * 100
    return round(percentual, 1)

# ===========================
# PERGUNTAS POR ESPÉCIE
# ===========================
perguntas_caes = [
    "Meu cão tem pouca energia",
    "O apetite do meu cão reduziu",
    "Meu cão reluta para levantar",
    "Meu cão gosta de estar perto de mim",
    "Meu cão foi brincalhão",
    "Meu cão mostrou uma quantidade normal de afeto",
    "Meu cão gostou de ser tocado ou acariciado",
    "Meu cão fez as suas atividades favoritas",
    "Meu cão dormiu bem durante a noite",
    "Meu cão agiu normalmente",
    "Meu cão teve problemas para levantar-se ou deitar-se",
    "Meu cão teve problemas para caminhar",
    "Meu cão caiu ou perdeu o equilíbrio",
    "Meu cão comeu normalmente a sua comida favorita",
    "Meu cão teve problemas para ficar confortável"
]

perguntas_gatos = [
    "Meu gato salta para cima",
    "Meu gato salta até a altura do balcão da cozinha ou alturas similares de uma só vez",
    "Meu gato pula para baixo",
    "Meu gato brinca com brinquedos e/ou persegue objetos",
    "Meu gato brinca e interage com outros animais de estimação",
    "Meu gato levanta-se de uma posição de descanso",
    "Meu gato deita-se e/ou senta-se",
    "Meu gato espreguiça-se",
    "Meu gato se limpa normalmente"
]

# ===========================
# SELEÇÃO DE ESPÉCIE
# ===========================
col1, col2 = st.columns([3, 1])

with col1:
    especie = st.radio("Selecione a espécie do seu pet:", ["Cão", "Gato"])

    respostas = []
    if especie == "Cão":
        st.subheader("Avaliação de dor para cães")
        for pergunta in perguntas_caes:
            valor = st.slider(pergunta, 0, 7, 0)
            respostas.append(valor)
        escala_max = 7
    else:
        st.subheader("Avaliação de dor para gatos")
        for pergunta in perguntas_gatos:
            valor = st.slider(pergunta, 0, 4, 0)
            respostas.append(valor)
        escala_max = 4

    # ===========================
    # CÁLCULO E ALERTA
    # ===========================
    if st.button("Calcular Avaliação de Dor"):
        percentual = calcular_dor(respostas, escala_max)
        st.markdown(f"### Resultado: **{percentual}% de dor**")

        if percentual >= 70:
            st.error("🚨 Dor intensa detectada! Procure um veterinário imediatamente.")
        elif percentual >= 40:
            st.warning("⚠️ Dor moderada detectada. Reavalie o pet e, se possível, consulte um veterinário.")
        else:
            st.success("✅ Sem dor ou dor leve detectada.")

        st.info("Um relatório foi enviado automaticamente para relatorio@petdor.app.")

# ===========================
# JANELA DE PROPAGANDAS
# ===========================
banners = [
    {"nome": "Iranimal", "url": "https://www.iranimal.com.br", "imagem": "https://via.placeholder.com/300x100?text=Iranimal"},
    {"nome": "Vital Pet Care", "url": "https://ccvitalpetcare.com.br", "imagem": "https://via.placeholder.com/300x100?text=Vital+Pet+Care"},
    {"nome": "Dejodonto", "url": "https://www.dejodonto.com.br", "imagem": "https://via.placeholder.com/300x100?text=Dejodonto"},
    {"nome": "Qualivita Pet", "url": "https://petqualivita.com.br", "imagem": "https://via.placeholder.com/300x100?text=Qualivita+Pet"}
]

# Cria área lateral
with col2:
    st.markdown("### 🐕 Parceiros")
    banner_placeholder = st.empty()

    def mostrar_banners():
        while True:
            for banner in banners:
                with banner_placeholder.container():
                    st.image(banner["imagem"], use_container_width=True)
                    st.markdown(
                        f"<div style='text-align:center;'><a href='{banner['url']}' target='_blank'>{banner['nome']}</a></div>",
                        unsafe_allow_html=True
                    )
                time.sleep(5)

    # Thread para trocar banners sem travar a interface
    threading.Thread(target=mostrar_banners, daemon=True).start()


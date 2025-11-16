"""
📝 Página de Avaliação de Dor - Design Wellness
Integra sistema modular de espécies (especies/)
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import json
import os

# Importa sistema modular de espécies
from especies import get_especies_nomes, get_especie_config, get_escala_labels
from database.models import salvar_avaliacao
from utils.pdf_generator import gerar_relatorio_pdf
from config import get_nivel_dor

def render_avaliacao_page(usuario):
    """Renderiza página de avaliação com design wellness"""

    # Header da página
    st.markdown("""
    <div class="wellness-card" style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #2d3748; margin-bottom: 0.5rem;">📝 Nova Avaliação</h1>
        <p style="color: #718096; font-size: 1.1rem;">
            Avalie o bem-estar do seu paciente com precisão científica
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Informações do paciente
    st.markdown("""
    <div class="wellness-card">
        <h3 style="color: #2d3748; margin-bottom: 1.5rem;">🐾 Dados do Paciente</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        nome_pet = st.text_input(
            "🐕 Nome do Paciente",
            placeholder="Ex: Rex, Luna, Max...",
            help="Nome do animal a ser avaliado"
        )

    with col2:
        especies = get_especies_nomes()
        especie = st.selectbox(
            "🦴 Espécie",
            especies,
            help="Selecione a espécie do paciente"
        )

    with col3:
        idade = st.number_input(
            "📅 Idade (anos)",
            min_value=0.0,
            max_value=30.0,
            value=5.0,
            step=0.5,
            help="Idade aproximada do animal"
        )

    # Carrega configuração da espécie
    if not nome_pet.strip():
        st.info("👆 Preencha o nome do paciente para continuar")
        return

    try:
        config = get_especie_config(especie)
    except KeyError:
        st.error(f"❌ Configuração para '{especie}' não encontrada")
        return

    # Instruções específicas da espécie
    st.markdown(f"""
    <div class="wellness-card">
        <h4 style="color: #2d3748; margin-bottom: 1rem;">📋 Instruções para {especie}</h4>
        <div style="background: linear-gradient(135deg, #AEE3FF, #C7F9CC); 
                    padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <strong>Escala:</strong> {config.escala_min} a {config.escala_max} | 
            <strong>Perguntas:</strong> {len(config.perguntas | 
            <strong>Tempo:</strong> ~5 minutos
        </div>
        <p style="color: #4a5568; line-height: 1.6;">
            {config.descricao}<br><br>
            <strong>Dicas importantes:</strong><br>
            • Avalie o comportamento nas últimas 24-48 horas<br>
            • Compare com o comportamento normal do paciente<br>
            • Seja objetivo e honesto nas respostas<br>
            • Em caso de dúvida, consulte literatura especializada
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Labels da escala
    labels_escala = config.get_labels_escala()

    with st.expander("📊 Legenda da Escala", expanded=False):
        st.markdown("""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
        """, unsafe_allow_html=True)

        for valor, label in labels_escala.items():
            st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem; 
                       background: rgba(174, 227, 255, 0.3); 
                       border-radius: 8px; border: 1px solid #AEE3FF;">
                <strong style="font-size: 1.2rem; color: #2d3748;">valor}</strong><br>
                <span style="color: #4a5568; font-size: 0.9rem;">{label}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Questionário principal
    st.markdown("""
    <div class="wellness-card">
        <h3 style="color: #2d3748; margin-bottom: 1.5rem;">🩺 Questionário de Avaliação</h3>
    </div>
    """, unsafe_allow_html=True)

    # Barra de progresso
    progress_bar = st.progress(0)
    progress_text = st.empty()

    respostas = []
    pontuacao_total = 0

    # Container para perguntas
    perguntas_container = st.container()

    with perguntas_container:
        for idx, pergunta in enumerate(config.perguntas, 1):
            # Atualiza progresso
            progress = idx / len(config.perguntas)
            progress_bar.progress(progress)
            progress_text.text(f"Avaliação: Pergunta {idx} de {len(config.perguntas)}")

            # Card da pergunta
            st.markdown(f"""
            <div class="wellness-card" style="margin-bottom: 1.5rem; padding: 1.5rem;">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <div style="background: linear-gradient(135deg, #AEE3FF, #C7F9CC); 
                               width: 40px; height: 40px; border-radius: 50%; 
                               display: flex; align-items: center; justify-content: center; 
                               margin-right: 1rem; font-weight: bold; color: #2d3748;">
                        {idx}
                    </div>
                    <h4 style="color: #2d3748; margin: 0;">{pergunta.texto}</h4>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Slider da resposta
            resposta = st.slider(
                label="",
                min_value=config.escala_min,
                max_value=config.escala_max,
                value=config.escala_min,
                step=1,
                key=f"pergunta_{idx}_{nome_pet}_{especie}",
                help=f"Selecione na escala {config.escala_min}-{config.escala_max}"
            )

            # Mostra label da resposta
            label_resposta = labels_escala.get(resposta, str(resposta))
            col1, col2 = st.columns([3, 1])
            with col1                st.caption(f"Selecionado: **{label_resposta}**")
            with col2:
                # Indicador visual da resposta
                if resposta <= 1:
                    st.markdown("🟢", unsafe_allow_html=True)
                elif resposta <= 3:
                    st.markdown("🟡", unsafe_allow_html=True)
                else:
                    st.markdown("🟠", unsafe_allow_html=True)

            # Calcula pontuação (inverte se necessário)
            if pergunta.invertida:
                pontos = config.escala_max - resposta
            else:
                pontos = resposta

            respostas.append(resposta)
            pontuacao_total += pontos

            # Separador
            if idx < len(config.perguntas):
                st.markdown("---")

    # Limpa progresso
    progress_bar.empty()
    progress_text.empty()

    # Botão de calcular resultado
    st.markdown("<br>", unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns([3, 1])

    with col_btn1:
        if st.button("🔍 Calcular Avaliação", type="primary", use_container_width=True):
            # Calcula resultados finais
            pontuacao_maxima = config.get_pontuacao_maxima()
            percentual = config.calcular_percentual(pontuacao_total)
            nivel = get_nivel_dor(percentual)

            # Exibe resultado principal
            st.markdown("""
            <div class="wellness-card" style="text-align: center; margin: 2rem 0;">
                <h2 style="color: #2d3748; margin-bottom: 1rem;">📊 Resultado da Avaliação</h2>
            </div>
            """, unsafe_allow_html=True)

            # Card do resultado principal
            cor_nivel = "#28a745" if percentual < 30 else "#ffc107" if percentual < 60 else "#dc3545"

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {cor_nivel}, {cor_nivel}); 
                       color: white; border-radius: 20px; padding: 2rem; 
                       text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
                <div style="font-size: 4rem; margin-bottom: 1rem;">{percentual:.1f}%</div>
                <h3 style="margin: 0.5rem 0; font-size: 1.5rem;">Nível de Dor Estimado</h3>
                <p style="margin: 1rem 0; font-size: 1.1rem;">
                    {nome_pet} • {especie} • {idade} anos
                </p>
                <div style="font-size: 1.2rem; font-weight: 600; margin-top: 1rem;">
                    {pontuacao_total}/{pontuacao_maxima} pontos
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Recomendação
            st.markdown("""
            <div class="wellness-card" style="margin: 2rem 0;">
                <h4 style="color: #2d3748; margin-bottom: 1rem;">💡 Recomendação Clínica</h4>
                <div style="padding: 1rem; background: rgba(199, 249, 204, 0.3); 
                           border-radius: 10px; border-left: 4px solid #28a745;">
                    <p style="color: #2d3748; margin: 0; font-size: 1.1rem;">
                        {nivel_texto}
                    </p>
                </div>
            </div>
            """.format(nivel_texto=nivel['texto']), unsafe_allow_html=True)

            # Salvar e gerar PDF
            col_salvar, col_pdf = st.columns(2)

            with col_salvar:
                sucesso, msg = salvar_avaliacao(
                    usuario['id'], nome_pet, especie, 
                    respostas, pontuacao_total, 
                    pontuacao_maxima, percentual
                )

                if sucesso:
                    st.success("✅ Avaliação salva no histórico!")
                    st.balloons()
                else:
                    st.error(f"❌ Erro ao salvar: {msg}")

            with col_pdf:
                try:
                    pdf_path = gerar_relatorio_pdf(
                        pet_nome=nome_pet,
                        especie=especie,
                        percentual=percentual,
                        pontuacao_total=pontuacao_total,
                        pontuacao_maxima=pontuacao_maxima,
                        usuario_nome=usuario['nome'],
                        idade=idade
                    )

                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="📄 Baixar Relatório PDF",
                            data=pdf_file.read(),
                            file_name=f"petdor_{nome_pet}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            type="secondary"
                        )

                    # Limpa arquivo temporário
                    os.unlink(pdf_path)

                except Exception as e:
                    st.error(f"Erro ao gerar PDF: {e}")

            # Detalhamento das respostas
            with st.expander("📋 Detalhamento Respostas", expanded=True):
                st.markdown("""
                <div class="wellness-card">
                    <h4 style="color: #2d3748;">Análise por Pergunta</h4>
                </div>
                """, unsafe_allow_html=True)

                for idx, (pergunta, resposta) in enumerate(zip(config.perguntas, respostas), 1):
                    pontos = config.escala_max - resposta if pergunta.invertida else resposta
                    cor = "🟢" if pontos <= 2 else "🟡" if pontos <= 4 else "🟠"

                    st.markdown(f"""
                    <div style="display: flex; align-items: center; 
                               padding: 1rem; background: rgba(255,255,255,0.7); 
                               border-radius: 10px; margin-bottom: 0.5rem; 
                               border-left: 4px solid {cor == '🟢' and '#28a745' or cor == '🟡' and '#ffc107' or '#dc3545'};">
                        <div style="width: 30px; text-align: center; margin-right: 1rem;">
                            <strong>{idx}.</strong>
                        </div>
                        <div style="flex: 1;">
                            <strong style="color: #2d3748;">{pergunta.texto}</strong><br>
                            <span style="color: #4a5568;">Resposta: {resposta} ({labels_escala[resposta]})</span>
                        </div>
                        <div style="text-align: center; min-width: 80px;">
                            <div style="font-size: 1.2rem; font-weight: bold; color: #2d3748;">{pontos}</div>
                            <span style="color: #4a5568; font-size: 0.8rem;">pontos</span>
                            <div style="font-size: 1.5rem; margin-top: 0.5rem;">{cor}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    with col_btn2:
        if st.button("← Voltar ao Início", use_container_width=True):
            st.session_state["menu"] = "🏠 Início"
            st.rerun()

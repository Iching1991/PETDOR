"""
📊 Página de Histórico - Design Wellness
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from database.models import buscar_avaliacoes_usuario, deletar_avaliacao
from especies import get_especies_nomes

def render_historico_page(usuario):
    """Renderiza página de histórico com design wellness"""

    # Header
    st.markdown("""
    <div class="wellness-card" style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #2d3748; margin-bottom: 0.5rem;">📊 Histórico de Avaliações</h1>
        <p style="color: #718096; font-size: 1.1rem;">
            Acompanhe a evolução do bem-estar dos seus pacientes
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Busca avaliações
    avaliacoes = buscar_avaliacoes_usuario(usuario['id'])

    if not avaliacoes:
        st.markdown("""
        <div class="wellness-card" style="text-align: center; padding: 3rem;">
            <h3 style="color: #718096;">📝 Ainda não há avaliações</h3>
            <p style="color: #a0aec0; margin: 1rem 0;">
                Faça sua primeira avaliação para começar a acompanhar a evolução!
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📝 Nova Avaliação", type="primary", use_container_width=True):
            st.rerun()
        return

    # Estatísticas gerais
    total_avaliacoes = len(avaliacoes)
    pets_unicos = len(set(a['pet_nome'] for a in avaliacoes))
    especies_unicas = len(set(a['especie'] for a in avaliacoes))
    media_dor = sum(a['percentual'] for a in avaliacoes) / total_avaliacoes

    st.markdown("""
    <div class="wellness-card">
        <h3 style="color: #2d3748; margin-bottom: 1.5rem;">📈 Visão Geral</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total de Avaliações", total_avaliacoes)

    with col2:
        st.metric("Pacientes Únicos", pets_unicos)

    with col3:
        st.metric("Espécies", especies_unicas)

    with col4:
        delta_color = "normal" if media_dor < 30 else "inverse" if media_dor < 60 else "off"
        st.metric("Média de Dor", f"{media_dor:.1f}%")

    st.divider()

    # Filtros
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        periodo = st.selectbox(
            "📅 Período",
            ["Todas", "Últimos 7 dias", "Últimos 30 dias", "Últimos 90 dias"]
        )

    with col_f2:
        especie_filtro = st.selectbox(
            "🦴 Espécie",
            ["Todas"] + get_especies_nomes()
        )

    with col_f3:
        pet_filtro = st.selectbox(
            "🐾 Paciente",
            ["Todos"] + sorted(set(a['pet_nome'] for a in avaliacoes))
        )

    # Aplica filtros
    df = pd.DataFrame(avaliacoes)
    df['data_avaliacao'] = pd.to_datetime(df['data_avaliacao'])

    # Filtro de período
    if periodo != "Todas":
        dias = {"Últimos 7 dias": 7, "Últimos 30 dias": 30, "Últimos 90 dias": 90}
        cutoff = datetime.now() - timedelta(days=dias[periodo])
        df = df[df['data_avaliacao'] >= cutoff]

    # Filtro de espécie
    if especie_filtro != "Todas":
        df = df[df['especie'] == especie_filtro]

    # Filtro de pet
    if pet_filtro != "Todos":
        df = df[df['pet_nome'] == pet_filtro]

    if len(df) == 0:
        st.warning("⚠️ Nenhuma avaliação encontrada com os filtros selecionados")
        return

    # Gráfico de evolução
    st.markdown("""
    <div class="wellness-card">
        <h3 style="color: #2d3748; margin-bottom: 1rem;">📈 Evolução Temporal</h3>
    </div>
    """, unsafe_allow_html=True)

    df_sorted = df.sort_values('data_avaliacao')

    fig, ax = plt.subplots(figsize=(12, 5))

    # Linha principal
    ax.plot(df_sorted['data_avaliacao'], df_sorted['percentual'], 
            marker='o', linewidth=2, markersize=8, color='#2b8aef', label='Percentual de Dor')

    # Faixas de referência
    ax.axhspan(0, 30, alpha=0.2, color='green', label='Baixo')
    ax.axhspan(30, 60, alpha=0.2, color='orange', label='Moderado')
    ax.axhspan(60, 100, alpha=0.2, color='red', label='Alto')

    ax.set_xlabel('Data', fontsize=12)
    ax.set_ylabel('Percentual de Dor (%)', fontsize=12)
    ax.set_title('Evolução do Percentual de Dor', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')

    # Formata eixo X
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    plt.xticks(rotation=45)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

    st.divider()

    # Tabela de avaliações
    st.markdown("""
    <div class="wellness-card">
        <h3 style="color: #2d3748; margin-bottom: 1rem;">📋 Detalhamento</h3>
    </div>
    """, unsafe_allow_html=True)

    # Prepara dados para exibição
    df_display = df.copy()
    df_display['data_avaliacao'] = df_display['data_avaliacao'].dt.strftime('%d/%m/%Y %H:%M')

    # Adiciona coluna de status
    def get_status(percentual):
        if percentual < 30:
            return "🟢 Baixo"
        elif percentual < 60:
            return "🟡 Moderado"
        else:
            return "🔴 Alto"

    df_display['Status'] = df_display['percentual'].apply(get_status)

    # Seleciona e renomeia colunas
    df_display = df_display[['data_avaliacao', 'pet_nome', 'especie', 'percentual', 'Status', 'id']]
    df_display = df_display.rename(columns={
        'data_avaliacao': 'Data/Hora',
        'pet_nome': 'Paciente',
        'especie': 'Espécie',
        'percentual': 'Dor (%)'
    })

    # Exibe tabela interativa
    st.dataframe(
        df_display.drop('id', axis=1),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Dor (%)": st.column_config.ProgressColumn(
                "Dor (%)",
                format="%.1f%%",
                min_value=0,
                max_value=100
            )
        }
    )

    # Ações em lote
    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("🗑️ Gerenciar Avaliações"):
        st.warning("⚠️ Atenção: A exclusão é permanente e não pode ser desfeita")

        avaliacao_id = st.selectbox(
            "Selecione uma avaliação para excluir",
            options=df['id'].tolist(),
            format_func=lambda x: f"{df[df['id']==x]['pet_nome'].values[0]} - {df[df['id']==x]['data_avaliacao'].dt.strftime('%d/%m/%Y').values[0]}"
        )

        if st.button("🗑️ Excluir Avaliação Selecionada", type="secondary"):
            sucesso, msg = deletar_avaliacao(avaliacao_id, usuario['id'])

            if sucesso:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

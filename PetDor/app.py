"""
🐾 PET DOR - Sistema de Avaliação de Dor Animal
Arquivo principal da aplicação Streamlit

Estrutura modular:
- especies/ → Perguntas organizadas por espécie (caes.py, gatos.py, etc.)
- pages/ → Páginas da aplicação
- auth/ → Autenticação e segurança
- utils/ → Utilitários (PDF, email, validações)
- database/ → Modelos e conexão DB
"""

import streamlit as st
import logging
from datetime import datetime
import os

# ===========================
# Configuração de Logging
# ===========================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===========================
# Inicializa Banco de Dados
# ===========================
from database.connection import init_database
init_database()

# ===========================
# Importa Páginas
# ===========================
from pages import (
    login,
    cadastro,
    recuperar_senha,
    reset_senha,
    avaliacao,
    historico,
    conta
)

# ===========================
# Importa Utilitários
# ===========================
from especies import get_especies_nomes
from database.models import get_estatisticas_usuario

# ===========================
# Configuração da Página
# ===========================
st.set_page_config(
    page_title="🐾 PET DOR",
    page_icon="🐕",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/seu-usuario/petdor',
        'Report a bug': 'mailto:suporte@petdor.com',
        'About': '**PET DOR** - Sistema de Avaliação de Dor Animal v1.0'
    }
)

# ===========================
# CSS Customizado - Design Wellness
# ===========================
st.markdown("""
<style>
    /* Importa fontes */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Reset e base */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Header principal */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2d3748;
        text-align: center;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .subtitle {
        text-align: center;
        color: #718096;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Cards Wellness */
    .wellness-card {
        background: linear-gradient(135deg, rgba(174, 227, 255, 0.1), rgba(199, 249, 204, 0.1));
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(174, 227, 255, 0.3);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }

    .wellness-card:hover {
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }

    /* Métricas */
    .metric-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 10px rgba(102, 126, 234, 0.3);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Botões */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f7fafc 0%, #edf2f7 100%);
    }

    /* Inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        transition: border-color 0.3s ease;
    }

    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    /* Sliders */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #AEE3FF, #C7F9CC);
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(174, 227, 255, 0.2), rgba(199, 249, 204, 0.2));
        border-radius: 10px;
        font-weight: 600;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
    }

    /* Animações */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .wellness-card {
        animation: fadeIn 0.5s ease-out;
    }

    /* Responsividade */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }

        .metric-value {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ===========================
# Verifica Token de Reset na URL
# ===========================
query_params = st.query_params

# Se existe token de reset, vai direto para página de reset
if "token" in query_params:
    token = query_params["token"]
    reset_senha.render_reset_senha_page(token)
    st.stop()

# ===========================
# Inicialização do Session State
# ===========================
if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None

if "menu_atual" not in st.session_state:
    st.session_state["menu_atual"] = "🏠 Início"

usuario = st.session_state["usuario_logado"]

# ===========================
# USUÁRIO LOGADO - PAINEL PRINCIPAL
# ===========================
if usuario:
    # ===========================
    # Sidebar - Menu de Navegação
    # ===========================
    with st.sidebar:
        # Logo (se existir)
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=150)
        else:
            st.markdown("### 🐾 PET DOR")

        st.markdown("---")

        # Informações do usuário
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; 
                   background: linear-gradient(135deg, rgba(174, 227, 255, 0.3), rgba(199, 249, 204, 0.3));
                   border-radius: 10px; margin-bottom: 1rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">👤</div>
            <div style="font-weight: 600; color: #2d3748; margin-bottom: 0.3rem;">
                {usuario['nome']}
            </div>
            <div style="font-size: 0.85rem; color: #718096;">
                {usuario['tipo']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Menu de navegação
        st.markdown("### 📋 Navegação")

        menu_opcao = st.radio(
            "Menu",
            ["🏠 Início", "📝 Nova Avaliação", "📊 Histórico", "⚙️ Conta"],
            index=0,
            label_visibility="collapsed"
        )

        st.session_state["menu_atual"] = menu_opcao

        st.markdown("---")

        # Estatísticas rápidas
        stats = get_estatisticas_usuario(usuario['id'])

        if stats and stats.get('total_avaliacoes', 0) > 0:
            st.markdown("### 📊 Resumo")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Avaliações",
                    stats.get('total_avaliacoes', 0),
                    label_visibility="visible"
                )

            with col2:
                st.metric(
                    "Pacientes",
                    stats.get('total_pets', 0),
                    label_visibility="visible"
                )

            st.markdown("---")

        # Botão de logout
        if st.button("🚪 Sair", use_container_width=True, type="secondary"):
            st.session_state["usuario_logado"] = None
            st.session_state["menu_atual"] = "🏠 Início"
            st.rerun()

    # ===========================
    # Conteúdo Principal
    # ===========================

    # Header da página
    st.markdown('<h1 class="main-header">🐾 PET DOR</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Sistema de Avaliação de Dor Animal</p>', unsafe_allow_html=True)

    # Renderiza página baseada no menu
    if menu_opcao == "🏠 Início":
        # Dashboard inicial
        st.success(f"Olá, **{usuario['nome']}**! 👋")

        st.markdown("""
        <div class="wellness-card">
            <h3 style="color: #2d3748; margin-bottom: 1rem;">🎯 Bem-vindo ao PET DOR</h3>
            <p style="color: #4a5568; line-height: 1.6;">
                Sistema profissional de avaliação de dor em animais, baseado em escalas 
                científicas validadas. Escolha uma opção no menu para começar.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Estatísticas
        stats = get_estatisticas_usuario(usuario['id'])

        if stats and stats.get('total_avaliacoes', 0) > 0:
            st.markdown("""
            <div class="wellness-card">
                <h3 style="color: #2d3748; margin-bottom: 1.5rem;">📈 Suas Estatísticas</h3>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{stats.get('total_avaliacoes', 0)}</div>
                    <div class="metric-label">Avaliações</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #48bb78, #38a169);">
                    <div class="metric-value">{stats.get('total_pets', 0)}</div>
                    <div class="metric-label">Pacientes</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                media = stats.get('media_percentual', 0)
                cor = "#28a745" if media < 30 else "#ffc107" if media < 60 else "#dc3545"

                st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, {cor}, {cor});">
                    <div class="metric-value">{media:.1f}%</div>
                    <div class="metric-label">Média de Dor</div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        # Ações rápidas
        st.markdown("""
        <div class="wellness-card">
            <h3 style="color: #2d3748; margin-bottom: 1rem;">🚀 Ações Rápidas</h3>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📝 Nova Avaliação", use_container_width=True, type="primary"):
                st.session_state["menu_atual"] = "📝 Nova Avaliação"
                st.rerun()

        with col2:
            if st.button("📊 Ver Histórico", use_container_width=True):
                st.session_state["menu_atual"] = "📊 Histórico"
                st.rerun()

        # Informações sobre espécies disponíveis
        with st.expander("🦴 Espécies Disponíveis", expanded=False):
            especies = get_especies_nomes()

            st.markdown(f"""
            **{len(especies)} espécies configuradas:**
            """)

            for especie in especies:
                st.markdown(f"• **{especie}**")

            st.info("💡 Cada espécie possui questionário e escala específicos validados cientificamente")

        # Sobre o sistema
        with st.expander("ℹ️ Sobre o PET DOR", expanded=False):
            st.markdown("""
            **PET DOR** é uma ferramenta profissional de triagem para avaliação de dor em animais.

            **✨ Funcionalidades:**
            - ✅ Questionários específicos por espécie
            - ✅ Escalas validadas cientificamente
            - ✅ Cálculo automático de percentual de dor
            - ✅ Histórico completo com gráficos evolutivos
            - ✅ Geração de relatórios profissionais em PDF
            - ✅ Sistema seguro de autenticação
            - ✅ Arquitetura modular (fácil adicionar espécies)

            **⚠️ Importante:** Esta ferramenta é de triagem e **não substitui** 
            a avaliação veterinária profissional.
            """)

    elif menu_opcao == "📝 Nova Avaliação":
        avaliacao.render_avaliacao_page(usuario)

    elif menu_opcao == "📊 Histórico":
        historico.render_historico_page(usuario)

    elif menu_opcao == "⚙️ Conta":
        conta.render_conta_page(usuario)

# ===========================
# USUÁRIO NÃO LOGADO - TELA DE ACESSO
# ===========================
else:
    # Header
    st.markdown('<h1 class="main-header">🐾 PET DOR</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Sistema de Avaliação de Dor Animal</p>', unsafe_allow_html=True)

    # Sidebar com menu
    with st.sidebar:
        st.markdown("### 🔐 Acesso ao Sistema")

        menu_opcao = st.radio(
            "Escolha uma opção:",
            ["🔑 Login", "📝 Cadastrar", "🔓 Recuperar Senha", "ℹ️ Sobre"],
            index=0,
            label_visibility="collapsed"
        )

    # Renderiza página baseada na seleção
    if menu_opcao == "🔑 Login":
        login.render_login_page()

    elif menu_opcao == "📝 Cadastrar":
        cadastro.render_cadastro_page()

    elif menu_opcao == "🔓 Recuperar Senha":
        recuperar_senha.render_recuperar_senha_page()

    elif menu_opcao == "ℹ️ Sobre":
        st.markdown("""
        <div class="wellness-card">
            <h2 style="color: #2d3748; margin-bottom: 1rem;">Sobre o PET DOR</h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        ### 🎯 O que é o PET DOR?

        **PET DOR** é uma ferramenta digital profissional para **avaliação de dor em animais de estimação**.
        Auxilia tutores e veterinários a identificar sinais de desconforto de forma objetiva e científica.

        ### 📊 Metodologia Científica

        O sistema utiliza questionários baseados em escalas validadas internacionalmente:

        - **🐕 Cães**: Escala 0-7
          - Baseado em: Canine Brief Pain Inventory (CBPI)
          - Glasgow Composite Pain Scale
          - 15 perguntas sobre comportamento, mobilidade, alimentação

        - **🐈 Gatos**: Escala 0-4
          - Baseado em: Feline Musculoskeletal Pain Index (FMPI)
          - 9 perguntas focadas em mobilidade vertical e autocuidado

        ### ✨ Funcionalidades

        - ✅ Questionários específicos por espécie
        - ✅ Cálculo automático de percentual de dor
        - ✅ Histórico completo com gráficos evolutivos
        - ✅ Relatórios profissionais em PDF
        - ✅ Sistema seguro de autenticação
        - ✅ Arquitetura modular (fácil expansão)

        ### 📈 Interpretação dos Resultados

        - **🟢 0-30%**: Baixa probabilidade de dor
        - **🟡 30-60%**: Dor moderada - monitorar
        - **🔴 60-100%**: Dor significativa - consultar veterinário

        ### ⚠️ Aviso Importante

        **Esta ferramenta é de triagem e NÃO substitui** a avaliação veterinária profissional.
        Em caso de sinais de dor, procure atendimento veterinário imediatamente.

        ### 🛠️ Tecnologia

        - **Frontend**: Streamlit
        - **Backend**: Python + SQLite
        - **Segurança**: bcrypt para senhas, tokens temporários
        - **Emails**: SMTP com SSL/TLS
        - **PDFs**: FPDF2
        - **Arquitetura**: Modular (subpasta `especies/` para fácil expansão)

        ### 📞 Suporte

        - **E-mail**: suporte@petdor.com
        - **GitHub**: github.com/seu-usuario/petdor

        ---

        © 2024 PET DOR - Todos os direitos reservados
        """)

# ===========================
# Footer Global
# ===========================
st.markdown("---")
st.markdown("""
<div style=': #a0aec0; font-size: 0.85rem; padding: 1rem 0;'>
    <strong>PET DOR</strong> - Sistema de Avaliação de Dor Animal v1.0<br>
    Desenvolvido com ❤️ para o bem-estar animal<br>
    <a href='mailto:suporte@petdor.com' style='color: #667eea;'>suporte@petdor.com</a>
</div>
""", unsafe_allow_html=True)

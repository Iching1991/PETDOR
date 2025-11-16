"""
⚙️ Página de Configurações da Conta
"""
import streamlit as st
from auth.user import deletar_usuario
from database.models import get_estatisticas_usuario

def render_conta_page(usuario):
    """Renderiza página de configurações da conta"""

    # Header
    st.markdown("""
    <div class="wellness-card" style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #2d3748; margin-bottom: 0.5rem;">⚙️ Minha Conta</h1>
        <p style="color: #718096; font-size: 1.1rem;">
            Gerencie suas informações e configurações
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Informações do usuário
    st.markdown("""
    <div class="wellness-card">
        <h3 style="color: #2d3748; margin-bottom: 1.5rem;">👤 Informações Pessoais</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Nome", value=usuario['nome'], disabled=True)
        st.text_input("Tipo de Usuário", value=usuario['tipo'], disabled=True)

    with col2:
        st.text_input("E-mail", value=usuario.get('email', 'N/A'), disabled=True)
        st.text_input("Membro desde", value=usuario.get('data_criacao', 'N/A'), disabled=True)

    st.divider()

    # Estatísticas da conta
    st.markdown("""
    <div class="wellness-card">
        <h3 style="color: #2d3748; margin-bottom: 1.5rem;">📊 Estatísticas da Conta</h3>
    </div>
    """, unsafe_allow_html=True)

    stats = get_estatisticas_usuario(usuario['id'])

    if stats and stats.get('total_avaliacoes', 0) > 0:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Avaliações Realizadas", stats.get('total_avaliacoes', 0))

        with col2:
            st.metric("Pacientes Únicos", stats.get('total_pets', 0))

        with col3:
            media = stats.get('media_percentual', 0)
            st.metric("Média de Dor", f"{media:.1f}%")
    else:
        st.info("Nenhuma avaliação realizada ainda")

    st.divider()

    # Zona de perigo
    st.markdown("""
    <div class="wellness-card" style="border-left: 4px solid #dc3545;">
        <h3 style="color: #dc3545; margin-bottom: 1rem;">⚠️ Zona de Perigo</h3>
        <p style="color: #718096;">
            Ações irreversíveis que afetam permanentemente sua conta
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🗑️ Excluir Conta", expanded=False):
        st.error("""
        **ATENÇÃO:** Esta ação é **PERMANENTE** e **IRREVERSÍVEL**!

        Ao excluir sua conta:
        - ❌ Todos os seus dados serão apagados
        - ❌ Todas as avaliações serão perdidas
        - ❌ Não será possível recuperar as informações
        """)

        st.markdown("<br>", unsafe_allow_html=True)

        confirmacao = st.text_input(
            "Digite **DELETAR** para confirmar a exclusão:",
            placeholder="DELETAR",
            help="Digite exatamente a palavra DELETAR em maiúsculas"
        )

        if st.button("🗑️ Confirmar Exclusão da Conta", type="secondary"):
            if confirmacao == "DELETAR":
                sucesso, msg = deletar_usuario(usuario['id'])

                if sucesso:
                    st.success(msg)
                    st.balloons()

                    # Desloga
                    del st.session_state["usuario_logado"]
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("⚠️ Digite DELETAR para confirmar")

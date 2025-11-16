"""
Página de Reset de Senha (via token da URL)
"""
import streamlit as st
from auth.password_reset import validar_token, resetar_senha
from utils.validators import validar_senha, senhas_conferem

def render_reset_senha_page(token):
    """Renderiza página de reset de senha"""

    st.markdown("""
    <div class="wellness-card" style="max-width: 500px; margin: 2rem auto;">
        <h2 style="color: #2d3748; text-align: center; margin-bottom: 1rem;">
            🔐 Redefinir Senha
        </h2>
        <p style="color: #718096; text-align: center; margin-bottom: 2rem;">
            Escolha uma nova senha segura
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Valida token primeiro
    usuario_id, erro = validar_token(token)

    if erro:
        st.error(f"❌ {erro}")
        st.info("Solicite um novo link de recuperação na opção **🔓 Recuperar Senha**")

        if st.button("← Voltar para Login"):
            st.query_params.clear()
            st.rerun()

        return

    # Formulário de nova senha
    with st.form("form_reset_senha"):
        nova_senha = st.text_input(
            "🔒 Nova Senha",
            type="password",
            placeholder="Mínimo 6 caracteres",
            help="Escolha uma senha segura"
        )

        confirma_senha = st.text_input(
            "🔒 Confirmar Nova Senha",
            type="password",
            placeholder="Digite novamente",
            help="Repita a nova senha"
        )

        submitted = st.form_submit_button(
            "Redefinir Senha",
            type="primary",
            use_container_width=True
        )

    if submitted:
        # Validações
        valid, msg = validar_senha(nova_senha)
        if not valid:
            st.error(f"❌ {msg}")
            return

        valid, msg = senhas_conferem(nova_senha, confirma_senha)
        if not valid:
            st.error(f"❌ {msg}")
            return

        # Reseta senha
        with st.spinner("Redefinindo senha..."):
            sucesso, mensagem = resetar_senha(token, nova_senha)

        if sucesso:
            st.success(f"✅ {mensagem}")
            st.balloons()

            # Limpa token da URL
            st.query_params.clear()

            st.info("Você pode fazer login agora com sua nova senha")

            if st.button("Ir para Login", type="primary"):
                st.rerun()
        else:
            st.error(f"❌ {mensagem}")

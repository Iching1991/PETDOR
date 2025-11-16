"""
Página de Login
"""
import streamlit as st
from auth.user import autenticar

def render_login_page():
    """Renderiza página de login"""

    st.markdown("""
    <div class="wellness-card" style="max-width: 500px; margin: 2rem auto;">
        <h2 style="color: #2d3748; text-align: center; margin-bottom: 2rem;">
            🔑 Login
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # Formulário de login
    with st.form("form_login", clear_on_submit=False):
        email = st.text_input(
            "📧 E-mail",
            placeholder="seu-email@exemplo.com",
            help="Digite seu e-mail cadastrado"
        )

        senha = st.text_input(
            "🔒 Senha",
            type="password",
            placeholder="••••••••",
            help="Digite sua senha"
        )

        col1, col2 = st.columns([3, 1])

        with col1:
            submitted = st.form_submit_button(
                "Entrar",
                type="primary",
                use_container_width=True
            )

        with col2:
            if st.form_submit_button("Limpar", use_container_width=True):
                st.rerun()

    if submitted:
        if not email or not senha:
            st.warning("⚠️ Preencha todos os campos")
            return

        # Tenta autenticar
        with st.spinner("Autenticando..."):
            usuario = autenticar(email, senha)

        if usuario:
            st.session_state["usuario_logado"] = usuario
            st.success(f"✅ Bem-vindo(a), **{usuario['nome']}**!")
            st.balloons()
            st.rerun()
        else:
            st.error("❌ E-mail ou senha incorretos")

    # Link para recuperar senha
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem;">
        <p style="color: #718096;">
            Esqueceu sua senha? Use a opção <strong>🔓 Recuperar Senha</strong> no menu lateral.
        </p>
    </div>
    """, unsafe_allow_html=True)

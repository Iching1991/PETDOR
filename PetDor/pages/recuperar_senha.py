"""
Página de Recuperação de Senha
"""
import streamlit as st
from auth.password_reset import gerar_token_reset
from utils.validators import validar_email

def render_recuperar_senha_page():
    """Renderiza página de recuperação de senha"""

    st.markdown("""
    <div class="wellness-card" style="max-width: 500px; margin: 2rem auto;">
        <h2 style="color: #2d3748; text-align: center; margin-bottom: 1rem;">
            🔓 Recuperar Senha
        </h2>
        <p style="color: #718096; text-align: center; margin-bottom: 2rem;">
            Enviaremos um link de redefinição para seu e-mail
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Formulário
    with st.form("form_recuperar", clear_on_submit=False):
        email = st.text_input(
            "📧 E-mail Cadastrado",
            placeholder="seu-email@exemplo.com",
            help="Digite o e-mail usado no cadastro"
        )

        submitted = st.form_submit_button(
            "Enviar Link de Recuperação",
            type="primary",
            use_container_width=True
        )

    if submitted:
        if not email:
            st.warning("⚠️ Digite seu e-mail")
            return

        valid, msg = validar_email(email)
        if not valid:
            st.error(f"❌ {msg}")
            return

        # Gera token e envia e-mail
        with st.spinner("Enviando e-mail..."):
            sucesso, mensagem = gerar_token_reset(email)

        if sucesso:
            st.success(f"✅ {mensagem}")
            st.info("""
            📧 **Verifique sua caixa de entrada** (e também a pasta de spam)

            O link expira em 1 hora.
            """)
        else:
            st.error(f"❌ {mensagem}")

    # Informações adicionais
    with st.expander("ℹ️ Não recebeu o e-mail?"):
        st.markdown("""
        **Verifique:**
        - Caixa de spam/lixo eletrônico
        - Se o e-mail está correto
        - Aguarde alguns minutos (pode demorar)

        **Limite de tentativas:**
        - Máximo 3 solicitações por dia
        - Link válido por 1 hora

        **Ainda com problemas?**
        Entre em contato: suporte@petdor.com
        """)

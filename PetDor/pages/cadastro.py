"""
Página de Cadastro
"""
import streamlit as st
from auth.user import cadastrar_usuario
from utils.validators import validar_email, validar_senha, validar_nome, senhas_conferem

def render_cadastro_page():
    """Renderiza página de cadastro"""

    st.markdown("""
    <div class="wellness-card" style="max-width: 600px; margin: 2rem auto;">
        <h2 style="color: #2d3748; text-align: center; margin-bottom: 2rem;">
            📝 Criar Conta
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # Formulário de cadastro
    with st.form("form_cadastro", clear_on_submit=True):
        nome = st.text_input(
            "👤 Nome Completo",
            placeholder="Ex: Dr. João Silva",
            help="Digite seu nome completo"
        )

        email = st.text_input(
            "📧 E-mail",
            placeholder="seu-email@exemplo.com",
            help="Será usado para login e recuperação de senha"
        )

        col1, col2 = st.columns(2)

        with col1:
            senha = st.text_input(
                "🔒 Senha",
                type="password",
                placeholder="Mínimo 6 caracteres",
                help="Escolha uma senha segura"
            )

        with col2:
            confirma_senha = st.text_input(
                "🔒 Confirmar Senha",
                type="password",
                placeholder="Digite novamente",
                help="Repita a senha"
            )

        tipo = st.selectbox(
            "👨‍⚕️ Tipo de Usuário",
            ["Veterinário", "Tutor", "Clínica", "Estudante"],
            help="Selecione seu perfil"
        )

        # Termos de uso
        aceite = st.checkbox(
            "Li e aceito os termos de uso e política de privacidade",
            help="É necessário aceitar para criar conta"
        )

        submitted = st.form_submit_button(
            "Criar Conta",
            type="primary",
            use_container_width=True
        )

    if submitted:
        # Validações
        if not aceite:
            st.warning("⚠️ Você precisa aceitar os termos de uso")
            return

        valid, msg = validar_nome(nome)
        if not valid:
            st.error(f"❌ {msg}")
            return

        valid, msg = validar_email(email)
        if not valid:
            st.error(f"❌ {msg}")
            return

        valid, msg = validar_senha(senha)
        if not valid:
            st.error(f"❌ {msg}")
            return

        valid, msg = senhas_conferem(senha, confirma_senha)
        if not valid:
            st.error(f"❌ {msg}")
            return

        # Tenta cadastrar
        with st.spinner("Criando sua conta..."):
            sucesso, mensagem = cadastrar_usuario(nome, email, senha, tipo)

        if sucesso:
            st.success(f"✅ {mensagem}")
            st.balloons()
            st.info("📧 Verifique seu e-mail para confirmar o cadastro")
        else:
            st.error(f"❌ {mensagem}")

    # Link para login
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem;">
        <p style="color: #718096;">
            Já tem uma conta? Use a opção <strong>🔑 Login</strong> no menu lateral.
        </p>
    </div>
    """, unsafe_allow_html=True)

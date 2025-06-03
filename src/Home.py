from helper_methods import initialize_application, show_sidebar
import streamlit as st


initialize_application()
show_sidebar()


# Function to display the Home page
st.markdown("<h3>🤖 Bem-vindo(a) à aplicação RAG!</h3><br>", unsafe_allow_html=True)

st.write(
    "Aqui você consegue gerenciar seus projetos de IA e conversar com o assistente virtual."
)

st.write("Se tiver alguma dúvida de como usar a ferramenta, veja a página de FAQ.")

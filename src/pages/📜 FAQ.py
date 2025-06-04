from helper_methods import initialize_application, show_sidebar
import streamlit as st

# Setup
initialize_application()
show_sidebar()


def faq_page():
    st.title("FAQ - Perguntas Frequentes")
    st.write("Clique em uma pergunta para ver a resposta.")

    faq_data = [
        (
            "O que é o RAG?",
            "É uma ferramenta de Chatbot conversacional que utiliza a técnica RAG (Retrieval-Augmented Generation) para responder perguntas de usuários com base nos documentos fornecidos.",
        ),
        (
            "Como faço para cadastrar uma nova aplicação?",
            "Na aba 'Aplicações', clique no botão 'Cadastrar Nova Aplicação', preencha os dados necessários, envie os documentos e depois clique em 'Salvar'. Sua aplicação será listada na página de Chatbots.",
        )
    ]

    # iterate question and answer
    for pergunta, resposta in faq_data:
        with st.expander(pergunta):
            st.write(resposta)


faq_page()

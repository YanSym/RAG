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
            "O que é RAG (Retrieval-Augmented Generation)?",
            "RAG é uma técnica que combina a recuperação de informações (através de um banco de dados vetorial) com a geração de texto através de um LLMs (Large Language Models). Ele busca dados relevantes em uma base antes de gerar a resposta, garantindo maior precisão e contextualização na resposta do Chatbot.",
        ),
        (
            "Qual a diferença entre um Chatbot tradicional e um Chatbot com RAG?",
            "Um Chatbot tradicional responde apenas com base no modelo de linguagem (LLM) em que foi treinado, enquanto um com RAG busca informações em uma base externa antes de gerar a resposta.",
        ),
        (
            "Como faço para cadastrar uma nova aplicação?",
            "Na aba 'Aplicações', clique no botão 'Cadastrar Nova Aplicação', preencha os dados necessários, envie os documentos e depois clique em 'Salvar'. Sua aplicação será listada na página de Chatbots.",
        ),
        (
            "Como posso desligar uma aplicação que não está mais em uso?",
            "Caso queira desligar uma aplicação, comunique o time da QADS",
        ),
        (
            "Como posso visualizar os Dashboards e métricas da ferramenta?",
            "Vá até a aba 'Dashboards', onde você encontrará gráficos e estatísticas relevantes sobre o uso do Chatbot..",
        ),
        (
            "O Chatbot consegue responder perguntas sobre qualquer assunto?",
            "Não! Ele responde com base em conhecimentos gerais e nos documentos disponíveis no sistema. Se a resposta não for encontrada, o modelo pode não responder ou então gerar uma resposta pouco precisa.",
        ),
        (
            "Os dados carregados são atualizados em tempo real?",
            "Não! Para inserir novas informações, deve ser cadastrada uma nova aplicação.",
        ),
        (
            "O chatbot pode ser integrado a outras plataformas?",
            "No momento, não. Porém, caso haja necessidade, comunique o time da QADS para priorizar a atividade.",
        ),
        (
            "Como faço para relatar um problema ou sugerir uma melhorias?",
            "Mande um email para o time da QADS com a sua sugestão.",
        ),
    ]

    # iterate question and answer
    for pergunta, resposta in faq_data:
        with st.expander(pergunta):
            st.write(resposta)


faq_page()

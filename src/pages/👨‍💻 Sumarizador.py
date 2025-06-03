import streamlit as st
import tempfile
import requests
import os

from helper_methods import initialize_application, show_sidebar, check_run_docker

# Setup
initialize_application()
show_sidebar()


# map origin
if check_run_docker():
    API_URL = os.getenv("API_URL", "http://fastapi:8000").split(",")[0]
else:
    API_URL = os.getenv("API_URL", "http://localhost:8000").split(",")[0]


# Streamlit UI
st.title("👨‍💻 Resumo de Documentos")

# UI elements
word_limit = st.number_input("Palavras do resumo", 50, 10000, 200)
additional_info = st.text_area("Informações adicionais")
summarize_all = st.radio("Metodologia de resumo", ["Todos", "Um por um"])
summarize_flag = summarize_all.strip() == "Todos"
uploaded_files = st.file_uploader(
    "Upload de arquivos", type=["pdf", "txt", "docx", "zip"], accept_multiple_files=True
)

if st.button("Gerar Resumo"):
    if uploaded_files:
        with tempfile.TemporaryDirectory() as temp_dir:
            files_to_send = []
            for file in uploaded_files:
                path = os.path.join(temp_dir, file.name)
                with open(path, "wb") as f:
                    f.write(file.read())

                # arquivo temporário
                with open(path, "rb") as f:
                    files_to_send.append(("files", (file.name, f.read())))

            # api request
            try:
                response = requests.post(
                    f"{API_URL}/summarize/",
                    data={
                        "word_limit": word_limit,
                        "summarize_all": summarize_flag,
                        "additional_info": additional_info,
                        "parameters": str(st.session_state["parameters"]),
                    },
                    files=files_to_send,
                )

                if response.status_code == 200:
                    summaries = response.json().get("summaries", {})
                    if len(summaries) == 0:
                        st.warning("Nenhum resumo encontrado.")
                    else:
                        st.subheader("Resumo")
                        for doc, summary in summaries.items():
                            if doc != "_All_Docs_":
                                if "/" in doc:
                                    doc = doc.split("/")[-1]
                                st.markdown(f"**📝 {doc}**")
                            st.write(summary)
                else:
                    st.error("Erro ao processar documentos.")

            except Exception:
                st.error("Erro na API de processamento.")
    else:
        st.warning("Envie ao menos um arquivo.")

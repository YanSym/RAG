from helper_methods import (
    initialize_application,
    show_sidebar,
    check_run_docker,
    convert_data,
    download_excel,
)
import streamlit as st
import requests
import os

# Setup
initialize_application()
show_sidebar()

# map origin
if check_run_docker():
    API_URL = os.getenv("API_URL", "http://fastapi:8000").split(",")[0]
else:
    API_URL = os.getenv("API_URL", "http://localhost:8000").split(",")[0]

st.title("📁 Análise de CVs com IA")

# Inputs
job_title = st.text_input("Título da Vaga")
job_description = st.text_area("Descrição da Vaga")

uploaded_files = st.file_uploader(
    "Carregar CVs (PDF ou ZIP com PDFs)",
    type=["pdf", "zip"],
    accept_multiple_files=True,
)

if st.button("Upload"):
    if not job_title:
        st.error("Por favor, digite o título da vaga.")
    elif not job_description:
        st.error("Por favor, digite a descrição da vaga.")
    elif not uploaded_files:
        st.error("Por favor, carregue ao menos um arquivo.")
    else:
        with st.spinner("Processando arquivos..."):
            # Prepare files for POST request
            files_data = [
                ("files", (f.name, f.getbuffer(), f.type)) for f in uploaded_files
            ]

            payload = {
                "job_title": job_title,
                "job_description": job_description,
                "parameters": str(st.session_state["parameters"]),
            }

            try:
                response = requests.post(
                    f"{API_URL}/recrutamento/",
                    data=payload,
                    files=files_data,
                    timeout=120,  # adjust if needed
                )
            except requests.exceptions.RequestException as e:
                st.error(f"Erro na comunicação com o backend: {e}")
                st.stop()

            if response.status_code == 200:
                resp_json = response.json()
                if "data" in resp_json and resp_json["data"]:
                    data = resp_json["data"]
                    df = convert_data(data)
                    if len(df) == 0:
                        st.warning(
                            "Nenhum candidato válido foi encontrado nos arquivos."
                        )
                        st.stop()
                    else:
                        st.dataframe(df)
                        st.download_button(
                            label="Download Excel",
                            data=download_excel(df),
                            file_name="avaliacao_candidatos.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )
                else:
                    st.error("Nenhum dado retornado do backend.")
            else:
                st.error(
                    f"Erro no processamento dos arquivos: {response.status_code} - {response.text}"
                )

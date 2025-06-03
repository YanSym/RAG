from helper_methods import (
    initialize_application,
    show_sidebar,
    decrypt_password,
    PROJECTS_DIR,
)
from helper_rag import ChatBot
from typing import List, Dict
from datetime import datetime
import streamlit as st
from gtts import gTTS
import json
import os


# Setup
initialize_application()
show_sidebar()

# Cria diretório para áudios se não existir
AUDIO_DIR = "static_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Streamlit UI
st.title("🤖 Aplicação RAG")


def get_projects() -> List[str]:
    try:
        return [
            d
            for d in os.listdir(PROJECTS_DIR)
            if os.path.isdir(os.path.join(PROJECTS_DIR, d))
        ]
    except Exception:
        return []


def save_log(project_name, user_input, result_text) -> None:
    """Logs a single chatbot interaction to a JSONL file."""
    try:
        log_path = os.path.join(PROJECTS_DIR, project_name, "logs")
        os.makedirs(log_path, exist_ok=True)

        log_file = os.path.join(log_path, f"chat_log_{datetime.now().date()}.jsonl")
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "bot_response": result_text,
        }

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def chatbot_page() -> None:
    projects = get_projects()
    if not projects:
        st.write(
            "Nenhum projeto foi encontrado. Por favor, crie um projeto antes de usar o chatbot."
        )
        return

    project_name = st.selectbox("Projeto:", [""] + projects)
    if project_name == "":
        st.write("\nPor favor, selecione um projeto para começar.")
        return

    # parameters
    parameters = st.session_state["parameters"]

    if "chatbots" not in st.session_state:
        st.session_state["chatbots"] = {}

    if project_name not in st.session_state["chatbots"]:
        project_path = os.path.join(PROJECTS_DIR, project_name)
        metadata_path = os.path.join(project_path, "metadata.json")
        PASSWORD_ADMIN = parameters["admin"]

        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            flag_password = metadata["flag_password"]
            project_password = decrypt_password(metadata["password"].strip()).strip()

        # if password
        if flag_password:
            password = st.text_input("Senha do projeto:", type="password")
        else:
            password = ""

        if st.button("Iniciar Chatbot"):
            password_input = password.strip()

            # Check if the password is required and if it is empty
            if flag_password and password_input == "":
                st.error("Por favor, digite a senha do projeto.")
                return

            # Check if the password is correct
            if (
                flag_password
                and password_input != project_password
                and password_input != PASSWORD_ADMIN
            ):
                st.error("Senha incorreta.")
                return

            # Initialize the chatbot application
            chatbot = ChatBot(project_name)
            st.session_state["chatbots"][project_name] = {
                "chatbot": chatbot,
                "messages": [
                    {
                        "role": "assistant",
                        "content": chatbot.TEXT_ENTER_CHAT,
                    }
                ],
                "last_docs": [],  # Inicializa vazio
            }

    if project_name in st.session_state["chatbots"]:

        # Create two columns for temperature and debug mode side by side
        col1, col2, _, _, _ = st.columns([1, 1, 1, 1, 1])

        # Debug mode
        with col1:
            debug_mode = st.radio(
                "🐞Modo Debug?",
                ["Não", "Sim"],
                horizontal=True,
                key="radio_debug",
            )

        # LLM temperature
        with col2:
            temperature = st.slider(
                "Temperatura:", min_value=0.0, max_value=1.0, value=0.0, step=0.1
            )
            temperature = float(temperature)

        bot: ChatBot = st.session_state["chatbots"][project_name]["chatbot"]
        list_messages: List[Dict[str, str]] = st.session_state["chatbots"][
            project_name
        ]["messages"]

        for message in list_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        user_input = st.chat_input("Digite sua mensagem...")

        if user_input and user_input != "":
            st.session_state["chatbots"][project_name]["messages"].append(
                {"role": "user", "content": user_input}
            )
            with st.chat_message("user"):
                st.write(user_input)

        list_messages = st.session_state["chatbots"][project_name]["messages"]
        if list_messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Gerando resposta..."):
                    result_dict = bot.generate_response(
                        user_input, temperature, debug_mode
                    )
                    response = result_dict["Response"]
                    st.write(response)

                    # Update documents
                    docs = result_dict.get("Documents", [])
                    st.session_state["chatbots"][project_name]["last_docs"] = docs

                    # Save log to text
                    save_log(project_name, user_input, result_dict)

            st.session_state["chatbots"][project_name]["messages"].append(
                {"role": "assistant", "content": response}
            )

            st.session_state["last_response_text"] = response

        # Mostrar documentos relacionados SOMENTE se houver
        docs = st.session_state["chatbots"][project_name].get("last_docs", [])
        if docs:
            frase = (
                "Documento relacionado" if len(docs) == 1 else "Documentos relacionados"
            )
            with st.expander(frase, expanded=False):
                for path in docs:
                    try:
                        full_path = os.path.join(
                            PROJECTS_DIR, project_name, "files", path
                        )
                        with open(full_path, "rb") as f:
                            data = f.read()
                            file_name = os.path.basename(path)
                            st.download_button(
                                label=f"{file_name}",
                                data=data,
                                file_name=file_name,
                                mime="application/octet-stream",
                            )
                    except FileNotFoundError:
                        st.warning(f"Arquivo não encontrado: {path}")

        # Geração e reprodução de áudio
        if "last_response_text" in st.session_state:
            audio_button_key = f"audio_btn_{len(list_messages)}"

            if parameters["flag_audio"] and st.button(
                "🔊 Ouvir resposta", key=audio_button_key
            ):
                try:
                    response_text = st.session_state["last_response_text"]
                    audio_path = os.path.join(
                        AUDIO_DIR,
                        f"audio_{project_name}_{datetime.now().timestamp()}.mp3",
                    )
                    tts = gTTS(text=response_text, lang="pt-br")
                    tts.save(audio_path)
                    st.session_state["last_audio_path"] = audio_path
                except Exception as e:
                    st.warning(f"Erro ao gerar áudio: {e}")

        if "last_audio_path" in st.session_state:
            st.audio(st.session_state["last_audio_path"], format="audio/mp3")


chatbot_page()

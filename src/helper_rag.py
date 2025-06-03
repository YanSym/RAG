from prompts.prompts import (
    PROMPT_CHATBOT,
    PROMPT_GUARDRAIL,
    PROMPT_REGULAR_REPLY,
    PROMPT_KB,
    TEXT_END_PROMPT,
    TEXT_CANT_REPLY,
    TEXT_ENTER_CHAT,
)
from helper_methods import PROJECTS_DIR
from parameters.offensive_words import LIST_OFFENSIVE_WORDS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from unidecode import unidecode
from typing import List
from openai import OpenAI
import streamlit as st
import re
import os


class ChatBot:
    """
    A chatbot for handling user interactions, retrieving relevant documents,
    and generating AI responses using OpenAI's LLM and FAISS for vector-based retrieval.
    """

    def __init__(self, project_name: str) -> None:
        """
        Initializes the ChatBot with project-specific settings.

        Args:
            project_name (str): Name of the project to load FAISS database.
        """
        self.PROJECTS_DIR = PROJECTS_DIR
        self.project_name = project_name
        self.parameters = st.session_state["parameters"]
        self.kb_path = os.path.join(self.PROJECTS_DIR, project_name, "KB.txt")
        self.faiss_path = os.path.join(self.PROJECTS_DIR, project_name, "faiss_db")
        self.prompt_path = os.path.join(
            self.PROJECTS_DIR, project_name, "prompts", "prompt_app.txt"
        )
        self.TEXT_ENTER_CHAT = TEXT_ENTER_CHAT
        self.flag_debug = self.parameters["debug"]
        self.prompt_bot = self.get_prompt()

        try:
            with st.spinner("Carregando..."):

                # KB
                if os.path.exists(self.kb_path):
                    with open(self.kb_path, "r", encoding="utf-8") as file:
                        self.KB = str(file.read()).strip()
                    self.embedding_model = None
                    self.vectorstore = None

                # Context (vector DB)
                else:
                    self.KB = None
                    encode_kwargs = {"normalize_embeddings": False}
                    self.embedding_model = HuggingFaceEmbeddings(
                        model_name=self.parameters["embedding"],
                        encode_kwargs=encode_kwargs,
                    )

                    self.vectorstore = FAISS.load_local(
                        self.faiss_path,
                        self.embedding_model,
                        allow_dangerous_deserialization=True,
                    )
        except Exception as e:
            st.error(f"Erro ao carregar o chatbot: {project_name} | {e}")

    def get_prompt(self) -> str:
        """
        Retrieves the prompt for the chatbot from a file or returns a default prompt.
        If the prompt file does not exist, it returns a default prompt defined in `PROMPT_CHATBOT`.

        Returns:
            str: The prompt string.
        """
        try:
            if os.path.exists(self.prompt_path):
                with open(self.prompt_path, "r", encoding="utf-8") as file:
                    prompt_app = str(file.read()).strip()
                    prompt_app = f"{prompt_app}\n{TEXT_END_PROMPT}"
                    return prompt_app
            return PROMPT_CHATBOT
        except Exception:
            return PROMPT_CHATBOT

    def check_guardrail(self, text: str) -> bool:
        """
        Checks if the input text contains offensive content or violates safety guidelines.

        Args:
            text (str): The user's input text.

        Returns:
            bool: True if the text is safe, False if it violates guidelines.
        """
        text_clean = unidecode(text.lower())

        for word in LIST_OFFENSIVE_WORDS:
            if re.search(rf"\b{word}\b", text_clean):
                return False

        client = OpenAI(api_key=self.parameters["key"])
        response = client.chat.completions.create(
            model=self.parameters["model_name"],
            temperature=0,
            messages=[{"role": "user", "content": PROMPT_GUARDRAIL.format(text=text)}],
        )
        llm_decision = response.choices[0].message.content.strip()
        return llm_decision == "SIM"

    def get_relevant_documents(self, query: str) -> List[str]:
        """
        Retrieves relevant documents from the FAISS vector store based on similarity search.

        Args:
            query (str): The user's query.

        Returns:
            List[str]: A list of relevant document contents.
        """
        num_docs_max = int(self.parameters["MAX_DOCS"])
        try:
            if not self.vectorstore:
                return []

            docs_with_scores = self.vectorstore.similarity_search_with_score(
                query, k=num_docs_max
            )

            # filtered docs
            filtered_docs = [
                [doc, score]
                for doc, score in docs_with_scores
                if score <= self.parameters["similarity_threshold"]
            ]

            # top docs
            top_docs = [
                {
                    "document": doc.metadata["source"],
                    "content": doc.page_content,
                    "score": score,
                }
                for doc, score in sorted(filtered_docs, key=lambda x: x[1])[
                    :num_docs_max
                ]
            ]

            return top_docs
        except Exception:
            return None

    def llm_regular_reply(self, text: str, temperature: float) -> str:
        """
        Generates a response from the LLM without additional context.

        Args:
            text (str): The user's input text.
            temperature (float): Temperature setting for the LLM response.

        Returns:
            str: The AI-generated response.
        """
        parameters = st.session_state["parameters"]
        client = OpenAI(api_key=self.parameters["key"])
        response = client.chat.completions.create(
            model=parameters["model_name"],
            temperature=temperature,
            messages=[
                {"role": "user", "content": PROMPT_REGULAR_REPLY.format(question=text)}
            ],
        )
        # return response.choices[0].message.content.strip()
        self.used_gpt_api = True
        self.api_raw_output = response.choices[0].message.content.strip()
        return self.api_raw_output

    def llm_kb_reply(self, input_text: str, temperature: float) -> str:
        """
        Generates a response from the LLM using the provided context.

        Args:
            input_text (str): The user's input text.
            temperature (float): Temperature setting for the LLM response.

        Returns:
            str: The AI-generated response.
        """
        parameters = st.session_state["parameters"]
        client = OpenAI(api_key=self.parameters["key"])
        response = client.chat.completions.create(
            model=parameters["model_name"],
            temperature=temperature,
            messages=[
                {
                    "role": "user",
                    "content": PROMPT_KB.format(question=input_text, KB=self.KB),
                }
            ],
        )

        return response.choices[0].message.content.strip()

    def llm_context_reply(
        self, input_text: str, context: str, temperature: float
    ) -> str:
        """
        Generates a response from the LLM using the provided context.

        Args:
            input_text (str): The user's input text.
            context (str): Additional contextual information retrieved from documents.
            temperature (float): Temperature setting for the LLM response.

        Returns:
            str: The AI-generated response.
        """
        parameters = st.session_state["parameters"]
        client = OpenAI(api_key=self.parameters["key"])
        prompt_format = self.prompt_bot.format(question=input_text, context=context)
        response = client.chat.completions.create(
            model=parameters["model_name"],
            temperature=temperature,
            messages=[
                {
                    "role": "user",
                    "content": prompt_format,
                }
            ],
        )
        return response.choices[0].message.content.strip()

    def generate_response(
        self, input_text: str, temperature: float, debug_mode: str
    ) -> str:
        """
        Generates a chatbot response based on user input, applying guardrails and context retrieval if needed.

        Args:
            input_text (str): The user's query.
            temperature (float): Temperature setting for the LLM response.
            debug_mode (str): Debug mode flag to control debug output.

        Returns:
            str: The chatbot's response or a fallback message if the input is deemed unsafe.
        """
        if self.check_guardrail(input_text):
            if self.flag_debug or debug_mode == "Sim":
                st.write("🐞 Debug: Resposta bloqueada pelo guardrail!")

                return {
                    "Response_Type": "0_GUARDRAIL_BLOCK",
                    "Response": TEXT_CANT_REPLY,
                    "Context": "",
                    "Documents": [],
                }

        if self.KB:
            if self.flag_debug or debug_mode == "Sim":
                st.write("🐞 Debug: Respondendo usando KB.")

            return {
                "Response_Type": "1_KB",
                "Response": self.llm_kb_reply(input_text, temperature),
                "Context": "",
                "Documents": [],
            }

        # get relevant documents
        relevant_contexts = self.get_relevant_documents(input_text)

        if not relevant_contexts:
            if self.flag_debug or debug_mode == "Sim":
                st.write("🐞 Debug: Respondendo sem contexto específico.")

            return {
                "Response_Type": "2_Regular",
                "Response": self.llm_regular_reply(input_text, temperature),
                "Context": "",
                "Documents": [],
            }

        # build context
        context = self.build_context(relevant_contexts)
        if self.flag_debug or debug_mode == "Sim":
            st.write(f"🐞 Debug: Contexto encontrado:\n\n{context}\n\n")

        # generate response
        response = self.llm_context_reply(input_text, context, temperature)
        if response.strip() == "Desculpe, não consigo te ajudar com essa informação.":
            list_documents = []
            context = ""
        else:
            documents = [doc["document"] for doc in relevant_contexts]
            list_documents = list(dict.fromkeys(documents))

        # return the response with context and documents
        return {
            "Response_Type": "3_Contextual",
            "Response": response,
            "Context": context,
            "Documents": list_documents,
        }

    def build_context(self, relevant_contexts):
        """Builds a context string from the relevant documents retrieved."""
        context = ""
        if len(relevant_contexts) > 0:
            for dict_items in relevant_contexts:
                document = dict_items["document"]
                content = dict_items["content"]
                context += f"Documento: {document}\n"
                context += (
                    f"### Início do conteúdo do documento: {document}\n{content}\n"
                )
                context += f"### Fim do documento: {document}\n\n"
        return context

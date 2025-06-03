# RAG Chatbot Application with Streamlit and Langchain

## Overview
The goal of this project is to develop a **domain-specific application** that combines the strengths of a **Large Language Model (LLM)** with the **efficiency of a vector database** for data storage and retrieval. Using **Retrieval-Augmented Generation (RAG)** for the method and **Streamlit** for the front-end, the application is built with Python.

## Technology Stack:
- **Frontend**: Streamlit for building the user interface.
- **Vector Database**: FAISS for efficient data storage and retrieval. 
- **LLM**: OpenAI model for natural language processing and query handling.
- **Backend**: LangChain framework utilizing the RAG method.

## Project Structure
- **src/**: Contains Python-based chatbot script and Streamlit main script.
- **src/materials/**: Contains data that our model will use to answer questions.
- **report/**: Stores [Report](report) files.
- **.env**: Contains API keys.

## Dependencies
- Python 3.12+
- langchain
- python-dotenv
- streamlit
- pypdf

## Usage
1. Clone the repository
2. Navigate to the project directory
3. Install dependencies: `pip install -r requirements.txt`
4. Set up your LLM by filling "key" inside the artifacts.yaml file.
5. Navigate to src directory: `cd src`
6. Run the Streamlit application: `streamlit run Home.py`
7. Open your web browser and navigate to the URL provided by Streamlit.
8. Interact with the chatbot by typing messages and receiving responses from the local LLM service.

## To run remote:
docker run -d --restart always -p 8501:8501 --name streamlit_app rag
docker ps

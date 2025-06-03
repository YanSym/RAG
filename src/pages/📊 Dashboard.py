from helper_methods import initialize_application, show_sidebar, PROJECTS_DIR
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import json
import os

# Setup
initialize_application()
show_sidebar()

st.header("📊 Dashboard: Estatísticas dos Projetos")
st.write("")
st.write("")


def load_project_metadata():
    """Loads metadata for all projects from the projects directory."""
    try:
        projects = []
        for project_name in os.listdir(PROJECTS_DIR):
            project_path = os.path.join(PROJECTS_DIR, project_name)
            metadata_path = os.path.join(project_path, "metadata.json")

            if os.path.isdir(project_path) and os.path.exists(metadata_path):
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                    projects.append(metadata)

        return projects
    except Exception:
        return None


# Load project data
projects_metadata = load_project_metadata()

if not projects_metadata:
    st.warning("Nenhum projeto foi cadastrado ainda.")
else:
    # Convert to DataFrame
    df_projects = pd.DataFrame(projects_metadata)

    # Extract relevant data
    df_projects["creation_date"] = pd.to_datetime(df_projects["creation_date"])
    df_projects["num_files"] = df_projects["files"].apply(len)
    df_projects["total_words"] = df_projects["files"].apply(
        lambda x: sum(f["word_count"] for f in x)
    )
    df_projects["project_owner"] = df_projects["project_owner"].fillna("Desconhecido")

    # Basic statistics
    total_projects = df_projects.shape[0]
    total_files = df_projects["num_files"].sum()
    avg_word_count = df_projects["total_words"].mean()
    unique_owners = df_projects["project_owner"].nunique()

    # Add an introduction with an expander
    st.write(
        """
    Bem-vindo ao painel de controle de estatísticas dos projetos! Aqui você pode:
    - Visualizar estatísticas gerais dos projetos.
    - Explorar detalhes de cada projeto.
    - Analisar gráficos interativos sobre os dados dos projetos.
    """
    )

    # Wrap general statistics in an expander
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📂 Total de Projetos", total_projects)
    col2.metric("📄 Total de Arquivos", total_files)
    col3.metric("📝 Média de Palavras", f"{avg_word_count:.0f}")
    col4.metric("🧑 Donos de Projetos", unique_owners)

    # Project Overview Table
    with st.expander("📜 Visão Geral dos Projetos", expanded=False):
        st.write(
            "Nesta tabela, você pode visualizar informações detalhadas sobre cada projeto, como nome, responsável, data de criação, número de arquivos e total de palavras."
        )
        st.dataframe(
            df_projects[
                [
                    "project_name",
                    "project_owner",
                    "creation_date",
                    "num_files",
                    "total_words",
                ]
            ].rename(
                columns={
                    "project_name": "Nome do Projeto",
                    "project_owner": "Responsável",
                    "creation_date": "Data de Criação",
                    "num_files": "Total de Arquivos",
                    "total_words": "Palavras",
                }
            )
        )

    # Bar Chart - Number of files per project
    with st.expander("📊 Arquivos por Projeto", expanded=False):
        st.write(
            "O gráfico abaixo mostra a quantidade de arquivos por projeto, permitindo identificar rapidamente quais projetos possuem mais ou menos arquivos."
        )
        fig, ax = plt.subplots()
        df_projects.sort_values("num_files", ascending=False, inplace=True)
        ax.bar(df_projects["project_name"], df_projects["num_files"], color="green")
        ax.set_xlabel("Projetos")
        ax.set_ylabel("Número de Arquivos")
        ax.set_title("Número de Arquivos por Projeto")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)

    # Wrap "Palavras por Projeto" in an expander
    with st.expander("📏 Palavras por Projeto", expanded=False):
        st.write(
            "O gráfico abaixo mostra a quantidade de palavras por projeto, permitindo identificar a densidade de conteúdo em cada projeto."
        )
        fig, ax = plt.subplots()
        df_projects.sort_values("num_files", ascending=False, inplace=True)
        ax.bar(df_projects["project_name"], df_projects["total_words"], color="blue")
        ax.set_xlabel("Projetos")
        ax.set_ylabel("Quantidade de Palavras")
        ax.set_title("Quantidade de Palavras por Projeto")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)

    # Prepare data for "Evolução da Criação de Projetos"
    df_creation_timeline = (
        df_projects.groupby(df_projects["creation_date"].dt.to_period("M"))
        .size()
        .reset_index(name="count")
    )
    df_creation_timeline["creation_month"] = df_creation_timeline[
        "creation_date"
    ].dt.strftime("%Y-%m")

    # Wrap "Evolução da Criação de Projetos" in an expander
    with st.expander("⏳ Evolução da Criação de Projetos", expanded=False):
        st.write(
            "Este gráfico mostra a linha do tempo da criação de projetos, permitindo visualizar tendências ao longo do tempo."
        )
        fig, ax = plt.subplots()
        ax.plot(
            df_creation_timeline["creation_month"],
            df_creation_timeline["count"],
            marker="o",
            linestyle="-",
            color="purple",
        )
        ax.set_xlabel("Mês/Ano")
        ax.set_ylabel("Projetos Criados")
        ax.set_title("Linha do Tempo da Criação de Projetos")
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)

    # Owner-based statistics
    # Wrap "Projetos por Dono" in an expander
    with st.expander("📌 Projetos por Dono", expanded=False):
        st.write(
            "O gráfico abaixo mostra a distribuição de projetos por dono, permitindo identificar quais responsáveis possuem mais projetos."
        )
        df_owners = (
            df_projects.groupby("project_owner")
            .size()
            .reset_index(name="total_projects")
        )
        fig, ax = plt.subplots()
        ax.bar(df_owners["project_owner"], df_owners["total_projects"], color="orange")
        ax.set_xlabel("Donos de Projetos")
        ax.set_ylabel("Quantidade de Projetos")
        ax.set_title("Distribuição de Projetos por Dono")
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)

    # Wrap project details in an expander
    with st.expander("🔎 Detalhes do Projeto", expanded=False):
        project_selected = st.selectbox(
            "Selecione um projeto:", df_projects["project_name"]
        )

        if project_selected:
            selected_project = df_projects[
                df_projects["project_name"] == project_selected
            ].iloc[0]
            st.write(f"**Nome:** {selected_project['project_name']}")
            st.write(f"**Dono do Projeto:** {selected_project['project_owner']}")
            st.write(
                f"**Data de Criação:** {selected_project['creation_date'].strftime('%d/%m/%Y')}"
            )
            st.write(f"**Arquivos:** {selected_project['num_files']}")
            st.write(f"**Palavras no Projeto:** {selected_project['total_words']}")

            st.subheader("📁 Arquivos do Projeto")
            for file in selected_project["files"]:
                st.write(f"- {file['file_name']} ({file['word_count']} palavras)")

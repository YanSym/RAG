from concurrent.futures import ThreadPoolExecutor, as_completed
from helper_methods import get_llm_response
from prompts.prompts import PROMPT_CV
import tempfile
import zipfile
import PyPDF2
import json
import os


def extract_text_from_pdf(pdf_path: str) -> str:
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        return "".join(page.extract_text() for page in reader.pages)


def llm_extract_cv_details(
    cv_text: str, job_title: str, job_description: str, parameters: dict
) -> dict:
    prompt = (
        PROMPT_CV.replace("<titulo>", job_title)
        .replace("<descricao>", job_description)
        .replace("<cv_text>", cv_text)
    )
    response = get_llm_response(prompt, parameters, 0)

    try:
        return json.loads(response)
    except Exception:
        try:
            response = "{" + response.strip().split("{")[1].split("}")[0] + "}"
            return json.loads(response)
        except Exception as e:
            return {"error": f"JSON parse failed: {str(e)}", "raw": response}


def process_pdf(
    file_path: str, job_title: str, job_description: str, parameters: dict
) -> dict:
    try:
        cv_text = extract_text_from_pdf(file_path)
        return llm_extract_cv_details(cv_text, job_title, job_description, parameters)
    except Exception as e:
        return {"error": str(e)}


def process_cv_files(
    file_paths: list, job_title: str, job_description: str, parameters: dict
) -> list:
    all_pdfs = []

    for path in file_paths:
        if path.endswith(".zip"):
            with zipfile.ZipFile(path, "r") as zip_ref:
                extract_dir = tempfile.mkdtemp()
                zip_ref.extractall(extract_dir)
                pdfs = [
                    os.path.join(extract_dir, f)
                    for f in os.listdir(extract_dir)
                    if f.endswith(".pdf")
                ]
                all_pdfs.extend(pdfs)
        elif path.endswith(".pdf"):
            all_pdfs.append(path)

    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(process_pdf, pdf, job_title, job_description, parameters)
            for pdf in all_pdfs
        ]
        for future in as_completed(futures):
            results.append(future.result())

    return results

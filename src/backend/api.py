import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, APIRouter, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from backend.summarizer import Summarizer
from helper_methods import check_run_docker
from backend.recruit import process_cv_files
from typing import List
import tempfile
import shutil
import ast

app = FastAPI()

# CORS origins
if check_run_docker():
    origins = os.getenv("API_URL", "http://fastapi:8000").split(",")[0]
else:
    origins = os.getenv("API_URL", "http://localhost:8000").split(",")[0]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origins],  # Note: should be a list
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create routers
summarizer_router = APIRouter()
recruit_router = APIRouter()


# Summarize endpoint
@summarizer_router.post("/summarize/")
async def summarize_endpoint(
    word_limit: int = Form(...),
    summarize_all: bool = Form(...),
    additional_info: str = Form(""),
    parameters: str = Form(""),
    files: List[UploadFile] = File(...),
):
    try:
        parameters = ast.literal_eval(parameters)

        with tempfile.TemporaryDirectory() as temp_dir:
            file_paths = []
            for file in files:
                file_path = os.path.join(temp_dir, file.filename)
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)
                file_paths.append(file_path)

            summarizer = Summarizer(parameters)
            result = summarizer.process_documents(
                file_paths, word_limit, summarize_all, additional_info
            )

        return {"summaries": result}

    except Exception as e:
        return {"error": str(e)}


# Recrutamento endpoint
@recruit_router.post("/recrutamento/")
async def recrutamento_endpoint(
    job_title: str = Form(...),
    job_description: str = Form(...),
    parameters: str = Form(...),  # JSON string
    files: List[UploadFile] = File(...),
):
    try:
        parameters = ast.literal_eval(parameters)

        with tempfile.TemporaryDirectory() as temp_dir:
            file_paths = []
            for file in files:
                file_path = os.path.join(temp_dir, file.filename)
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)
                file_paths.append(file_path)

            result = process_cv_files(
                file_paths, job_title, job_description, parameters
            )

        return {"data": result}
    except Exception as e:
        return {"error": str(e)}


# Register routers with the app
app.include_router(summarizer_router)
app.include_router(recruit_router)

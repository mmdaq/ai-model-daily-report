import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

QQ_EMAIL = os.getenv("QQ_EMAIL", "")
QQ_SMTP_AUTH_CODE = os.getenv("QQ_SMTP_AUTH_CODE", "")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", QQ_EMAIL)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

SCHEDULE_HOUR = int(os.getenv("SCHEDULE_HOUR", "8"))
SCHEDULE_MINUTE = int(os.getenv("SCHEDULE_MINUTE", "0"))

DATABASE_PATH = BASE_DIR / "database" / "ai_models.db"
REPORT_TEMPLATE_DIR = BASE_DIR / "mail" / "templates"
DOCS_DIR = BASE_DIR / "docs"
DOCS_ARCHIVE_DIR = DOCS_DIR / "archive"

GITHUB_KEYWORDS = [
    "gguf",
    "llama.cpp",
    "flux",
    "comfyui",
    "wan2.1",
    "video model",
]

HF_SEARCH_TERMS = ["gguf", "lora", "diffusers", "video"]

COLLECTOR_LIMIT = 50
REQUEST_TIMEOUT = 30
MAX_MODELS_PER_CATEGORY = 15

MODELSCOPE_ORGS = [
    "Qwen",
    "AI-ModelScope",
    "deepseek-ai",
    "ZhipuAI",
    "iic",
    "OpenGVLab",
    "Tongyi-MAI",
]
MODELSCOPE_API = "https://www.modelscope.cn/api/v1/models/"

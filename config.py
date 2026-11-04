from pathlib import Path
import os

ADMIN_LOGIN = os.getenv("STUDYTRACK_ADMIN_LOGIN", "admin")
ADMIN_PASSWORD = os.getenv("STUDYTRACK_ADMIN_PASSWORD", "admin123")
CAMINHO_DB = Path(__file__).resolve().parent / "data" / "studytrack.json"
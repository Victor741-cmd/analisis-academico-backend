# backend/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import pandas as pd
from .analitica.analysis import cargar_excel, freqs, crosstabs
app = FastAPI(title="API Analisis Academico")

# Habilitar CORS para el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en prod, pon tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "Resultados.xlsx"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/summary")
def summary():
    df = cargar_excel(DATA_PATH)
    return {
        "frecuencias": freqs(df),
        "crosstabs": crosstabs(df),
        "total_respuestas": int(len(df)),
    }

@app.get("/summary/by-date")
def summary_by_date(start: str | None = None, end: str | None = None):
    df = cargar_excel(DATA_PATH)
    if start:
        df = df[df["marca_temporal"] >= pd.to_datetime(start)]
    if end:
        df = df[df["marca_temporal"] <= pd.to_datetime(end)]
    return {
        "frecuencias": freqs(df),
        "crosstabs": crosstabs(df),
        "total_respuestas": int(len(df)),
    }

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    out = DATA_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as f:
        f.write(await file.read())
    return {"message": "Archivo ha sido actualizado"}

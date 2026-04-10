# backend/main.py
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
try:
    from .analitica.analysis import cargar_excel, freqs, crosstabs, estadisticas
except ImportError:
    from analitica.analysis import cargar_excel, freqs, crosstabs, estadisticas

load_dotenv()

app = FastAPI(
    title="API Análisis Académico",
    description="Análisis descriptivo de encuestas sobre estrategias de lectura crítica y Saber Pro",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DATA_PATH: configurable por variable de entorno o fallback a ruta relativa por defecto
_default_data = Path(__file__).resolve().parent.parent / "anexo" / "data" / "Resultados.xlsx"
DATA_PATH = Path(os.getenv("DATA_PATH", str(_default_data)))


def _load_or_raise() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Archivo de datos no encontrado: {DATA_PATH}. "
                   "Use POST /upload para cargar el archivo o configure DATA_PATH.",
        )
    try:
        return cargar_excel(DATA_PATH)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error al leer el archivo: {exc}")


@app.get("/health", tags=["Sistema"])
def health():
    return {
        "status": "ok",
        "data_file": str(DATA_PATH),
        "data_exists": DATA_PATH.exists(),
    }


@app.get("/summary", tags=["Análisis"])
def summary():
    df = _load_or_raise()
    return {
        "total_respuestas": int(len(df)),
        "frecuencias": freqs(df),
        "crosstabs": crosstabs(df),
        "estadisticas": estadisticas(df),
    }


@app.get("/summary/by-date", tags=["Análisis"])
def summary_by_date(start: str | None = None, end: str | None = None):
    df = _load_or_raise()
    try:
        if start:
            df = df[df["marca_temporal"] >= pd.to_datetime(start)]
        if end:
            df = df[df["marca_temporal"] <= pd.to_datetime(end)]
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Formato de fecha inválido: {exc}")

    if df.empty:
        raise HTTPException(status_code=404, detail="No hay datos para el rango de fechas indicado.")

    return {
        "total_respuestas": int(len(df)),
        "frecuencias": freqs(df),
        "crosstabs": crosstabs(df),
        "estadisticas": estadisticas(df),
        "filtro": {"start": start, "end": end},
    }


@app.post("/upload", tags=["Datos"])
async def upload(file: UploadFile = File(...)):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos .xlsx")
    try:
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_PATH, "wb") as f:
            f.write(await file.read())
        # Validar que el archivo subido es legible
        _load_or_raise()
        return {"message": "Archivo actualizado correctamente", "path": str(DATA_PATH)}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error al guardar el archivo: {exc}")

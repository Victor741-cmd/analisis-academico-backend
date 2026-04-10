# backend/analitica/analysis.py
from pathlib import Path
import pandas as pd


COLUMNAS = [
    "marca_temporal",
    "relevancia_lectura",
    "frecuencia_estrategias",
    "utilidad_saber_pro",
    "acceso_ia",
    "interes_modelo_ml",
    "preparacion_estudiantes",
    "estrategia_mas_efectiva",
    "ampliar_a_otras_competencias",
    "mejora_competencia_con_ml",
]

VARIABLES_CATEGORICAS = COLUMNAS[1:]  # todas excepto marca_temporal


def cargar_excel(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, engine="openpyxl")

    if len(df.columns) < len(COLUMNAS):
        raise ValueError(
            f"El archivo debe tener al menos {len(COLUMNAS)} columnas; "
            f"se encontraron {len(df.columns)}."
        )

    rename_map = {df.columns[i]: COLUMNAS[i] for i in range(len(COLUMNAS))}
    df = df.rename(columns=rename_map)

    for c in VARIABLES_CATEGORICAS:
        df[c] = df[c].astype(str).str.strip()

    df["marca_temporal"] = pd.to_datetime(df["marca_temporal"], errors="coerce")
    return df


def _freq(series: pd.Series) -> list[dict]:
    ct = series.value_counts(dropna=False)
    pc = (ct / ct.sum() * 100).round(1)
    return pd.DataFrame({
        "categoria": ct.index.astype(str),
        "conteo": ct.values,
        "porcentaje": pc.values,
    }).to_dict("records")


def freqs(df: pd.DataFrame) -> dict:
    return {col: _freq(df[col]) for col in VARIABLES_CATEGORICAS}


def crosstabs(df: pd.DataFrame) -> dict:
    def ct(a: str, b: str) -> list[dict]:
        return (
            pd.crosstab(df[a], df[b], normalize="index")
            .round(3)
            .reset_index()
            .rename(columns={a: "categoria"})
            .to_dict("records")
        )

    return {
        "interes_vs_acceso": ct("interes_modelo_ml", "acceso_ia"),
        "utilidad_vs_relevancia": ct("utilidad_saber_pro", "relevancia_lectura"),
        "preparacion_vs_frecuencia": ct("preparacion_estudiantes", "frecuencia_estrategias"),
        "mejora_vs_interes": ct("mejora_competencia_con_ml", "interes_modelo_ml"),
    }


def estadisticas(df: pd.DataFrame) -> dict:
    result = {}
    for col in VARIABLES_CATEGORICAS:
        moda_val = df[col].mode()
        result[col] = {
            "moda": str(moda_val.iloc[0]) if not moda_val.empty else None,
            "n_categorias": int(df[col].nunique()),
            "n_respuestas": int(df[col].count()),
        }
    return result

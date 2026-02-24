# backend/analitica/analysis.py
from pathlib import Path
import pandas as pd

def cargar_excel(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, engine="openpyxl")

    rename_map = {
        df.columns[0]: "marca_temporal",
        df.columns[1]: "relevancia_lectura",
        df.columns[2]: "frecuencia_estrategias",
        df.columns[3]: "utilidad_saber_pro",
        df.columns[4]: "acceso_ia",
        df.columns[5]: "interes_modelo_ml",
        df.columns[6]: "preparacion_estudiantes",
        df.columns[7]: "estrategia_mas_efectiva",
        df.columns[8]: "ampliar_a_otras_competencias",
        df.columns[9]: "mejora_competencia_con_ml"
    }
    df = df.rename(columns=rename_map)

    for c in df.columns:
        if pd.api.types.is_object_dtype(df[c]) or pd.api.types.is_string_dtype(df[c]):
            df[c] = df[c].astype(str).str.strip()

    df["marca_temporal"] = pd.to_datetime(df["marca_temporal"], errors="coerce")
    return df

def _freq(series: pd.Series):
    ct = series.value_counts(dropna=False)
    pc = (ct / ct.sum() * 100).round(1)
    return pd.DataFrame({"categoria": ct.index, "conteo": ct.values, "porcentaje": pc.values})

def freqs(df: pd.DataFrame) -> dict:
    return {
        "relevancia_lectura": _freq(df["relevancia_lectura"]).to_dict("records"),
        "frecuencia_estrategias": _freq(df["frecuencia_estrategias"]).to_dict("records"),
        "utilidad_saber_pro": _freq(df["utilidad_saber_pro"]).to_dict("records"),
        "acceso_ia": _freq(df["acceso_ia"]).to_dict("records"),
        "interes_modelo_ml": _freq(df["interes_modelo_ml"]).to_dict("records"),
        "preparacion_estudiantes": _freq(df["preparacion_estudiantes"]).to_dict("records"),
        "estrategia_mas_efectiva": _freq(df["estrategia_mas_efectiva"]).to_dict("records"),
        "ampliar_a_otras_competencias": _freq(df["ampliar_a_otras_competencias"]).to_dict("records"),
        "mejora_competencia_con_ml": _freq(df["mejora_competencia_con_ml"]).to_dict("records"),
    }

def crosstabs(df: pd.DataFrame) -> dict:
    def ct(a, b):
        return pd.crosstab(df[a], df[b], normalize="index").round(2).reset_index().to_dict("records")
    return {
        "interes_vs_acceso": ct("interes_modelo_ml", "acceso_ia"),
        "utilidad_vs_relevancia": ct("utilidad_saber_pro", "relevancia_lectura"),
        "preparacion_vs_frecuencia": ct("preparacion_estudiantes", "frecuencia_estrategias"),
        "mejora_vs_interes": ct("mejora_competencia_con_ml", "interes_modelo_ml"),
    }
 

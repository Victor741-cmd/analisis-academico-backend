FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente del paquete
COPY . /app/analisis_academico_backend

# Crear directorio para los datos (se montará como volumen)
RUN mkdir -p /data

# Variable de entorno: ruta del archivo de datos dentro del contenedor
ENV DATA_PATH=/data/Resultados.xlsx

WORKDIR /app

EXPOSE 8000

CMD ["uvicorn", "analisis_academico_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# =====================================================
# Dockerfile para UDCito
# =====================================================

FROM python:3.11-slim

# Variables de entorno para debugging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY ./app /app/app/

# Crear usuario no privilegiado
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
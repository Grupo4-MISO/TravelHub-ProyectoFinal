FROM public.ecr.aws/docker/library/python:3.12-slim

# Evita generar archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias (opcional pero recomendado)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copiar el código
COPY . .

# Exponer puerto
EXPOSE 3003

# Ejecutar con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:3003", "main:app"]
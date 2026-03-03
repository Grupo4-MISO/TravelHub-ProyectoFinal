FROM public.ecr.aws/docker/library/python:3.12-slim

# Crear y usar el directorio de trabajo
WORKDIR /app

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del codigo
COPY . .

# Asegurar que el directorio de trabajo esta en PYTHONPATH
ENV PYTHONPATH=/app

# Puerto que usa la app
EXPOSE 3002

# Comando por defecto: Gunicorn sirviendo la app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3002"]
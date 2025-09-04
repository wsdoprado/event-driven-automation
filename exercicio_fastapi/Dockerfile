# Use Python 3.12 slim como base
FROM python:3.12-slim

# Diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da API
COPY . .

# Expõe a porta
EXPOSE 9000

# Inicia o FastAPI com uvicorn apontando para api_netbox_cache.py
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9000"]

FROM python:3.10-slim

# 1. Instalar herramientas del sistema (FFmpeg y RubberBand)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    rubberband-cli \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Truco anti-cuota: Instalar PyTorch CPU primero (~150 MB en vez de 2.5 GB)
COPY requirements.txt .
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 3. Instalar el resto de tus dependencias (Demucs ya no intentará bajar CUDA)
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiar el código de la aplicación
COPY . .

# 5. Crear carpetas de trabajo
RUN mkdir -p storage static

# 6. Exponer puerto oficial de Hugging Face Spaces
EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
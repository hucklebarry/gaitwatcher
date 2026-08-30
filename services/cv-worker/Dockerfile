FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
# Keep the optional YOLO backend CPU-only. PyPI's Linux torch packages may pull
# CUDA runtime packages, which are neither useful nor appropriate for this worker.
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.5.1 torchvision==0.20.1
RUN pip install --no-cache-dir -r requirements.txt
COPY *.py .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

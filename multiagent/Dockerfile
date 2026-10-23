FROM python:3.12-slim

WORKDIR /app

# Ensure unbuffered logs and default port
ENV PYTHONUNBUFFERED=1 \
    PORT=8080 \
    GOOGLE_GENAI_USE_VERTEXAI=True \
    GOOGLE_CLOUD_LOCATION=us-central1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose Cloud Run default port
EXPOSE 8080

# Start server
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8080"]

FROM python:3.8-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    poppler-utils \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip==23.3.2
RUN pip install -r requirements.txt

# Copy project files
COPY . .

EXPOSE 8000

CMD ["gunicorn", "job.wsgi:application", "--bind", "0.0.0.0:8000"]

# Base image with Python 3.11
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2

# Install curl and system dependencies
RUN apt-get update \
  && apt-get install -y curl build-essential libpq-dev \
  && apt-get clean

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
  && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Create and set working directory
WORKDIR /app
ENV PYTHONPATH=/app
# Copy Poetry files and install dependencies
COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Copy application code
COPY . /app

# Expose port
EXPOSE 8000

# Run the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

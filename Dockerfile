FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
     build-essential \
     libpq-dev \
     gettext \
     netcat-openbsd \
     && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create scripts directory if it doesn't exist and make scripts executable
RUN chmod +x scripts/*.sh

# Default command (will be overridden by docker-compose)
CMD ["bash"]

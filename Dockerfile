FROM python:3.9-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application files
COPY . .

# Create a non-root user
RUN useradd -ms /bin/bash stmuser
USER stmuser

CMD ["python", "main.py"]

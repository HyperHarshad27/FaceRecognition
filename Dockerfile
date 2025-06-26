# Use official Python image as base
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        libopenblas-dev \
        liblapack-dev \
        libx11-dev \
        libgtk-3-dev \
        libboost-python-dev \
        libboost-thread-dev \
        libsm6 \
        libxext6 \
        libgl1-mesa-glx \
        && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create required folders
RUN mkdir -p dataset logs && \
    touch logs/attendance.csv && \
    echo "Name,DateTime" > logs/attendance.csv

# Expose port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"] 
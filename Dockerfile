FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY autoclicker.py .
COPY config.json .

# Create log directory
RUN mkdir -p /app/logs

# Run the application
CMD ["python", "-u", "autoclicker.py"]

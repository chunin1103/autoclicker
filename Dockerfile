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

# Expose port (Koyeb will set PORT env variable)
EXPOSE 8000

# Run the application with gunicorn
CMD gunicorn autoclicker:app --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 120

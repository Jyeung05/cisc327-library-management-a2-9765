# Lightweight Python base image
FROM python:3.11-slim

# Ensure stdout/stderr are unbuffered for clearer logs
ENV PYTHONUNBUFFERED=1

# Create application directory
WORKDIR /app

# Install application dependencies first to leverage Docker layer caching
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose Flask default port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]

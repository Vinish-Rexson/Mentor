# Use the official Python image
FROM python:3.12.7-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files into the container
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the port the app runs on
EXPOSE 8000

# Use gunicorn as the WSGI server
CMD ["gunicorn", "project_name.wsgi:application", "--bind", "0.0.0.0:8000"]

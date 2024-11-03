# Use the official Python image as the base
FROM python:3.12.7-slim

# Set environment variables to prevent .pyc files and output buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set default environment variables for local development
# (Railway will override these with its own environment variables)
ENV DATABASE_NAME=your_local_database_name
ENV DATABASE_USER=your_local_user
ENV DATABASE_PASSWORD=your_local_password
ENV DATABASE_HOST=localhost
ENV DATABASE_PORT=5432

# Expose the port that the app runs on
EXPOSE 8000

# Run the Gunicorn server (collectstatic and migrate commands are handled in railway.json)
CMD ["gunicorn", "mentor_management.wsgi:application", "--bind", "0.0.0.0:8000"]

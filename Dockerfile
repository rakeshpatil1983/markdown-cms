FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY src/ ./src/

# Install dependencies
RUN pip install -e ".[dev]"

# Copy site content
COPY site/ ./site/

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "markdown_cms"]
